"""
Approval Handler for AI_agents

Handles human approval flow for checkpoints across multiple channels
(CLI, Slack, email, Linear comments).

Usage:
    from scripts.execution.approval_handler import ApprovalHandler

    handler = ApprovalHandler(config)

    # Send approval request
    request_id = handler.request_approval(checkpoint)

    # Wait for approval
    result = handler.wait_for_approval(request_id, timeout_minutes=60)

    if result.approved:
        continue_work()
"""

import os
import json
import time
import requests
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Callable, List
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import hashlib
import secrets


class ApprovalChannel(Enum):
    """Channels for approval requests"""
    CLI = "cli"
    SLACK = "slack"
    EMAIL = "email"
    LINEAR = "linear"
    WEBHOOK = "webhook"


class ApprovalStatus(Enum):
    """Status of an approval request"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMED_OUT = "timed_out"
    CANCELLED = "cancelled"


@dataclass
class ApprovalRequest:
    """Represents a pending approval request"""
    id: str
    checkpoint_id: str
    checkpoint_type: str
    created_at: datetime
    expires_at: Optional[datetime]
    context: Dict[str, Any]
    channels: List[ApprovalChannel]
    status: ApprovalStatus = ApprovalStatus.PENDING
    approval_token: Optional[str] = None  # For async approvals
    response: Optional[Dict[str, Any]] = None


@dataclass
class ApprovalResponse:
    """Response to an approval request"""
    approved: bool
    action: str  # "continue", "pause", "abort", "redirect"
    channel: ApprovalChannel
    responder: str
    timestamp: datetime
    notes: Optional[str] = None
    redirect_instructions: Optional[str] = None


class ApprovalHandler:
    """
    Handles multi-channel approval workflow.

    Supports:
    - CLI interactive approval
    - Slack buttons
    - Email magic links
    - Linear issue comments
    - Custom webhooks
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize approval handler.

        Args:
            config: Approval configuration from execution config
        """
        self.config = config
        self.notification_config = config.get("notification", {})
        self.timeout_minutes = config.get("timeout_minutes", 60)
        self.default_action = config.get("default_action", "pause")

        # State storage
        self.state_dir = Path(".ai-agents/state/approvals")
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Active requests
        self.active_requests: Dict[str, ApprovalRequest] = {}

        # Callback for async responses
        self.response_callback: Optional[Callable] = None

    def request_approval(
        self,
        checkpoint_id: str,
        checkpoint_type: str,
        context: Dict[str, Any],
        channels: Optional[List[ApprovalChannel]] = None
    ) -> str:
        """
        Create and send an approval request.

        Args:
            checkpoint_id: ID of the checkpoint
            checkpoint_type: Type of checkpoint
            context: Context data for the approval
            channels: Channels to use (defaults to config)

        Returns:
            Request ID
        """
        # Generate request ID and token
        request_id = f"ar-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{secrets.token_hex(4)}"
        approval_token = secrets.token_urlsafe(32)

        # Determine expiration
        expires_at = None
        if self.timeout_minutes > 0:
            expires_at = datetime.now() + timedelta(minutes=self.timeout_minutes)

        # Determine channels
        if channels is None:
            channels = self._get_configured_channels()

        # Create request
        request = ApprovalRequest(
            id=request_id,
            checkpoint_id=checkpoint_id,
            checkpoint_type=checkpoint_type,
            created_at=datetime.now(),
            expires_at=expires_at,
            context=context,
            channels=channels,
            approval_token=approval_token
        )

        self.active_requests[request_id] = request
        self._save_request(request)

        # Send to all channels
        for channel in channels:
            self._send_to_channel(request, channel)

        return request_id

    def _get_configured_channels(self) -> List[ApprovalChannel]:
        """Get channels configured for notifications."""
        channels = [ApprovalChannel.CLI]  # CLI always enabled

        if self.notification_config.get("slack_webhook"):
            channels.append(ApprovalChannel.SLACK)

        if self.notification_config.get("email"):
            channels.append(ApprovalChannel.EMAIL)

        if self.notification_config.get("linear_comment"):
            channels.append(ApprovalChannel.LINEAR)

        return channels

    def _send_to_channel(self, request: ApprovalRequest, channel: ApprovalChannel):
        """Send approval request to a specific channel."""
        try:
            if channel == ApprovalChannel.SLACK:
                self._send_slack(request)
            elif channel == ApprovalChannel.EMAIL:
                self._send_email(request)
            elif channel == ApprovalChannel.LINEAR:
                self._send_linear(request)
            elif channel == ApprovalChannel.WEBHOOK:
                self._send_webhook(request)
            # CLI is handled in wait_for_approval
        except Exception as e:
            print(f"Warning: Failed to send to {channel.value}: {e}")

    def _send_slack(self, request: ApprovalRequest):
        """Send Slack approval request with action buttons."""
        webhook_url = self.notification_config.get("slack_webhook")
        if not webhook_url or webhook_url.startswith("$"):
            return

        ctx = request.context
        expires_str = ""
        if request.expires_at:
            remaining = request.expires_at - datetime.now()
            expires_str = f" (expires in {int(remaining.total_seconds() / 60)} min)"

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🔔 Approval Required: {request.checkpoint_type.replace('_', ' ').title()}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Checkpoint ID:* `{request.checkpoint_id}`{expires_str}"
                }
            }
        ]

        # Add context fields
        fields = []
        if ctx.get("task_id"):
            fields.append({"type": "mrkdwn", "text": f"*Task:* {ctx['task_id']}"})
        if ctx.get("turn_number"):
            fields.append({"type": "mrkdwn", "text": f"*Turn:* {ctx['turn_number']}"})
        if ctx.get("context_usage"):
            fields.append({"type": "mrkdwn", "text": f"*Context:* {ctx['context_usage']*100:.0f}%"})

        if fields:
            blocks.append({"type": "section", "fields": fields})

        # Progress summary
        if ctx.get("progress_summary"):
            progress = ctx["progress_summary"]
            progress_text = " | ".join([f"{k}: {v}" for k, v in progress.items()])
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Progress:* {progress_text}"}
            })

        # Action buttons (using callback URL if available)
        # In production, these would link to an approval endpoint
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "✓ Continue"},
                    "style": "primary",
                    "action_id": "approve_continue",
                    "value": request.approval_token
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "⏸ Pause"},
                    "action_id": "approve_pause",
                    "value": request.approval_token
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "✗ Abort"},
                    "style": "danger",
                    "action_id": "approve_abort",
                    "value": request.approval_token
                }
            ]
        })

        # Add note about CLI fallback
        blocks.append({
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": f"_Or respond in CLI with request ID: `{request.id}`_"}
            ]
        })

        requests.post(webhook_url, json={"blocks": blocks})

    def _send_email(self, request: ApprovalRequest):
        """Send email approval request (placeholder - needs email service integration)."""
        email = self.notification_config.get("email")
        if not email:
            return

        # This would integrate with an email service like SendGrid, SES, etc.
        # For now, just log the intent
        print(f"[Email] Would send approval request to {email}")
        print(f"[Email] Request ID: {request.id}")
        print(f"[Email] Token: {request.approval_token}")

    def _send_linear(self, request: ApprovalRequest):
        """Add approval request as comment on Linear META issue."""
        # This would integrate with the state provider's Linear connection
        # For now, just log the intent
        print(f"[Linear] Would add approval comment for {request.id}")

    def _send_webhook(self, request: ApprovalRequest):
        """Send approval request to custom webhook."""
        webhook_url = self.notification_config.get("webhook_url")
        if not webhook_url:
            return

        payload = {
            "request_id": request.id,
            "checkpoint_id": request.checkpoint_id,
            "checkpoint_type": request.checkpoint_type,
            "context": request.context,
            "approval_token": request.approval_token,
            "expires_at": request.expires_at.isoformat() if request.expires_at else None
        }

        requests.post(webhook_url, json=payload)

    def wait_for_approval(
        self,
        request_id: str,
        timeout_override: Optional[int] = None
    ) -> ApprovalResponse:
        """
        Wait for approval response.

        Args:
            request_id: ID of the approval request
            timeout_override: Optional timeout override in minutes

        Returns:
            ApprovalResponse with the decision
        """
        request = self.active_requests.get(request_id)
        if not request:
            # Try to load from file
            request = self._load_request(request_id)
            if not request:
                raise ValueError(f"Unknown request ID: {request_id}")

        timeout = timeout_override if timeout_override is not None else self.timeout_minutes
        timeout_seconds = timeout * 60 if timeout > 0 else float('inf')

        start_time = time.time()

        # Check for async response first
        response = self._check_async_response(request_id)
        if response:
            return response

        # Fall back to CLI approval
        return self._cli_approval(request, timeout_seconds, start_time)

    def _cli_approval(
        self,
        request: ApprovalRequest,
        timeout_seconds: float,
        start_time: float
    ) -> ApprovalResponse:
        """Handle CLI-based approval."""
        print(self._format_cli_request(request))

        while True:
            elapsed = time.time() - start_time
            remaining = timeout_seconds - elapsed

            if remaining <= 0:
                return self._handle_timeout(request)

            # Check for async responses periodically
            response = self._check_async_response(request.id)
            if response:
                return response

            try:
                if timeout_seconds != float('inf'):
                    remaining_str = str(timedelta(seconds=int(remaining)))
                    prompt = f"\n[{remaining_str} remaining] Choice (c/p/a/d): "
                else:
                    prompt = "\nChoice (c/p/a/d): "

                choice = input(prompt).strip().lower()

                if choice == 'c':
                    return self._create_response(request, True, "continue", ApprovalChannel.CLI)
                elif choice == 'p':
                    return self._create_response(request, False, "pause", ApprovalChannel.CLI)
                elif choice == 'a':
                    confirm = input("Confirm abort? (y/n): ").strip().lower()
                    if confirm == 'y':
                        return self._create_response(request, False, "abort", ApprovalChannel.CLI)
                elif choice == 'd':
                    self._show_details(request)
                elif choice == 'r':
                    instructions = input("Enter redirect instructions: ").strip()
                    resp = self._create_response(request, True, "redirect", ApprovalChannel.CLI)
                    resp.redirect_instructions = instructions
                    return resp
                else:
                    print("Invalid choice. Use: c=continue, p=pause, a=abort, d=details, r=redirect")

            except KeyboardInterrupt:
                print("\n\nInterrupted")
                return self._create_response(request, False, "pause", ApprovalChannel.CLI, "Interrupted")

    def _format_cli_request(self, request: ApprovalRequest) -> str:
        """Format approval request for CLI display."""
        ctx = request.context

        lines = [
            "",
            "┌" + "─" * 60 + "┐",
            "│" + " APPROVAL REQUIRED ".center(60) + "│",
            "├" + "─" * 60 + "┤",
            f"│ Request ID: {request.id:<46} │",
            f"│ Type: {request.checkpoint_type.replace('_', ' ').title():<52} │",
        ]

        if request.expires_at:
            remaining = request.expires_at - datetime.now()
            expires_str = f"{int(remaining.total_seconds() / 60)} minutes"
            lines.append(f"│ Expires in: {expires_str:<46} │")

        lines.append("├" + "─" * 60 + "┤")

        if ctx.get("task_id"):
            lines.append(f"│ Task: {ctx['task_id']:<52} │")
        if ctx.get("turn_number"):
            lines.append(f"│ Turn: {ctx['turn_number']:<52} │")
        if ctx.get("context_usage"):
            lines.append(f"│ Context: {ctx['context_usage']*100:.1f}%{' ':<45} │")

        if ctx.get("progress_summary"):
            lines.append("│" + " " * 60 + "│")
            lines.append("│ Progress:" + " " * 50 + "│")
            for k, v in ctx["progress_summary"].items():
                lines.append(f"│   {k}: {v:<52} │")

        lines.extend([
            "├" + "─" * 60 + "┤",
            "│ Options:" + " " * 51 + "│",
            "│   [c] Continue" + " " * 45 + "│",
            "│   [p] Pause" + " " * 48 + "│",
            "│   [a] Abort" + " " * 48 + "│",
            "│   [d] Details" + " " * 46 + "│",
            "│   [r] Redirect with instructions" + " " * 25 + "│",
            "└" + "─" * 60 + "┘"
        ])

        return "\n".join(lines)

    def _show_details(self, request: ApprovalRequest):
        """Show detailed request information."""
        ctx = request.context

        print("\n" + "=" * 60)
        print("REQUEST DETAILS")
        print("=" * 60)
        print(f"Request ID: {request.id}")
        print(f"Checkpoint ID: {request.checkpoint_id}")
        print(f"Type: {request.checkpoint_type}")
        print(f"Created: {request.created_at.isoformat()}")
        if request.expires_at:
            print(f"Expires: {request.expires_at.isoformat()}")
        print(f"Channels: {', '.join(c.value for c in request.channels)}")

        print("\nContext:")
        for key, value in ctx.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            elif isinstance(value, list):
                print(f"  {key}: [{len(value)} items]")
            else:
                print(f"  {key}: {value}")

        print("=" * 60)

    def _handle_timeout(self, request: ApprovalRequest) -> ApprovalResponse:
        """Handle approval timeout."""
        action = self.default_action

        request.status = ApprovalStatus.TIMED_OUT
        self._save_request(request)

        approved = action == "continue"
        return self._create_response(
            request,
            approved,
            action,
            ApprovalChannel.CLI,
            "Approval timed out"
        )

    def _create_response(
        self,
        request: ApprovalRequest,
        approved: bool,
        action: str,
        channel: ApprovalChannel,
        notes: Optional[str] = None
    ) -> ApprovalResponse:
        """Create and save an approval response."""
        response = ApprovalResponse(
            approved=approved,
            action=action,
            channel=channel,
            responder="user" if channel == ApprovalChannel.CLI else channel.value,
            timestamp=datetime.now(),
            notes=notes
        )

        # Update request status
        request.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        request.response = {
            "approved": approved,
            "action": action,
            "channel": channel.value,
            "timestamp": response.timestamp.isoformat()
        }
        self._save_request(request)

        # Remove from active
        if request.id in self.active_requests:
            del self.active_requests[request.id]

        return response

    def _check_async_response(self, request_id: str) -> Optional[ApprovalResponse]:
        """Check for async response from Slack/webhook/etc."""
        response_file = self.state_dir / f"{request_id}_response.json"

        if response_file.exists():
            with open(response_file, 'r') as f:
                data = json.load(f)

            response_file.unlink()  # Remove after reading

            return ApprovalResponse(
                approved=data["approved"],
                action=data["action"],
                channel=ApprovalChannel(data["channel"]),
                responder=data.get("responder", "async"),
                timestamp=datetime.fromisoformat(data["timestamp"]),
                notes=data.get("notes")
            )

        return None

    def receive_async_response(
        self,
        request_id: str,
        token: str,
        approved: bool,
        action: str,
        channel: str,
        responder: Optional[str] = None
    ) -> bool:
        """
        Receive an async approval response (from webhook callback, etc.).

        Args:
            request_id: Request ID
            token: Approval token for verification
            approved: Whether approved
            action: Action to take
            channel: Channel that responded
            responder: Who responded

        Returns:
            True if response was accepted
        """
        request = self.active_requests.get(request_id)
        if not request:
            request = self._load_request(request_id)

        if not request or request.approval_token != token:
            return False

        # Save response for pickup
        response_file = self.state_dir / f"{request_id}_response.json"
        with open(response_file, 'w') as f:
            json.dump({
                "approved": approved,
                "action": action,
                "channel": channel,
                "responder": responder or channel,
                "timestamp": datetime.now().isoformat()
            }, f)

        return True

    def _save_request(self, request: ApprovalRequest):
        """Save request to file."""
        request_file = self.state_dir / f"{request.id}.json"
        with open(request_file, 'w') as f:
            json.dump({
                "id": request.id,
                "checkpoint_id": request.checkpoint_id,
                "checkpoint_type": request.checkpoint_type,
                "created_at": request.created_at.isoformat(),
                "expires_at": request.expires_at.isoformat() if request.expires_at else None,
                "context": request.context,
                "channels": [c.value for c in request.channels],
                "status": request.status.value,
                "approval_token": request.approval_token,
                "response": request.response
            }, f, indent=2)

    def _load_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Load request from file."""
        request_file = self.state_dir / f"{request_id}.json"
        if not request_file.exists():
            return None

        with open(request_file, 'r') as f:
            data = json.load(f)

        return ApprovalRequest(
            id=data["id"],
            checkpoint_id=data["checkpoint_id"],
            checkpoint_type=data["checkpoint_type"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            context=data["context"],
            channels=[ApprovalChannel(c) for c in data["channels"]],
            status=ApprovalStatus(data["status"]),
            approval_token=data.get("approval_token"),
            response=data.get("response")
        )

    def cancel_request(self, request_id: str) -> bool:
        """Cancel a pending approval request."""
        request = self.active_requests.get(request_id)
        if not request:
            request = self._load_request(request_id)

        if not request:
            return False

        request.status = ApprovalStatus.CANCELLED
        self._save_request(request)

        if request_id in self.active_requests:
            del self.active_requests[request_id]

        return True
