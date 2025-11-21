#!/usr/bin/env python3
"""
File-Based Multi-Agent Orchestrator

Production-ready orchestrator using team-communication.json for coordination.
This script demonstrates:
- File-based agent coordination
- Parallel task execution where possible
- Automatic blocker detection and resolution
- Manager-led integration

Usage:
    python file_based_orchestrator.py \\
        --project-dir /path/to/project \\
        --feature "shopping cart checkout"

The script expects:
- .ai-agents/state/team-communication.json to exist
- Agent configurations in .ai-agents/config.yml
- ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import asyncio

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

if not HAS_ANTHROPIC and not HAS_OPENAI:
    print("Error: Install 'anthropic' or 'openai': pip install anthropic")
    sys.exit(1)


class FileBasedOrchestrator:
    """
    Orchestrator that uses team-communication.json for coordination.

    This reads and writes to the communication file, just like agents do
    in a human-coordinated workflow, but automates the coordination.
    """

    def __init__(self, project_dir: str, api_provider: str = "anthropic"):
        self.project_dir = Path(project_dir)
        self.api_provider = api_provider
        self.communication_file = self.project_dir / ".ai-agents" / "state" / "team-communication.json"

        # Validate communication file exists
        if not self.communication_file.exists():
            raise FileNotFoundError(
                f"Communication file not found: {self.communication_file}\\n"
                "Please create it first. See PRACTICAL_WORKFLOW_GUIDE.md"
            )

        # Initialize API client
        if api_provider == "anthropic":
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            self.client = anthropic.Anthropic(api_key=api_key)
        elif api_provider == "openai":
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            self.client = openai.OpenAI(api_key=api_key)

        # Agent conversation histories
        self.conversations: Dict[str, List] = {}

    def read_communication_file(self) -> Dict:
        """Read current state from team-communication.json"""
        with open(self.communication_file, 'r') as f:
            return json.load(f)

    def write_communication_file(self, data: Dict):
        """Write updated state to team-communication.json"""
        data["last_updated"] = datetime.utcnow().isoformat() + "Z"
        with open(self.communication_file, 'w') as f:
            json.dump(data, f, indent=2)

    def call_agent(self, agent_id: str, role: str, prompt: str, system_prompt: str) -> str:
        """Call an agent via LLM API"""

        # Initialize conversation
        if agent_id not in self.conversations:
            self.conversations[agent_id] = []

        # Add message
        self.conversations[agent_id].append({
            "role": "user",
            "content": prompt
        })

        # Call API
        if self.api_provider == "anthropic":
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                system=system_prompt,
                messages=self.conversations[agent_id]
            )
            response = message.content[0].text

        elif self.api_provider == "openai":
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(self.conversations[agent_id])

            completion = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages
            )
            response = completion.choices[0].message.content

        # Save response
        self.conversations[agent_id].append({
            "role": "assistant",
            "content": response
        })

        return response

    def manager_create_tasks(self, feature_description: str):
        """Have manager create task breakdown and write to communication file"""

        print(f"\\n[Manager] Creating task breakdown...")

        comm_data = self.read_communication_file()

        system_prompt = """You are a Team Manager for a software development team.

Your job is to break down features into tasks and assign them to agents.

Available agents:
- backend-dev: Backend development (APIs, databases, services)
- frontend-dev: Frontend development (UI components, pages)
- qa-tester: Testing (unit tests, integration tests, E2E tests)

When creating tasks:
1. Make them specific and actionable
2. Identify dependencies
3. Assign to appropriate agent
4. Set realistic priorities

Respond with a JSON object containing the task breakdown."""

        prompt = f"""Please create a task breakdown for this feature:

{feature_description}

Current communication file state:
{json.dumps(comm_data, indent=2)}

Create 3-5 tasks and respond with ONLY valid JSON in this format:
{{
  "tasks": [
    {{
      "task_id": "TASK-001",
      "assigned_to": "backend-dev",
      "description": "Specific task description",
      "status": "not_started",
      "branch": "feature/name/agent/backend-dev/task",
      "priority": "high",
      "dependencies": [],
      "deliverables": ["List of expected outputs"]
    }}
  ],
  "decisions": [
    {{
      "decision": "Technical decision made",
      "rationale": "Why this decision",
      "affected_agents": ["agent-id"]
    }}
  ]
}}"""

        response = self.call_agent("manager", "team_manager", prompt, system_prompt)

        # Parse JSON response
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            json_str = response[start:end]
            task_data = json.loads(json_str)

            # Update communication file
            comm_data["current_feature"] = feature_description
            comm_data["manager_instructions"]["current_focus"] = feature_description
            comm_data["manager_instructions"]["active_tasks"] = task_data.get("tasks", [])
            comm_data["manager_instructions"]["decisions"] = task_data.get("decisions", [])

            self.write_communication_file(comm_data)

            print(f"  [Manager] Created {len(task_data.get('tasks', []))} tasks")
            for task in task_data.get("tasks", []):
                print(f"    - {task['task_id']}: {task['description'][:50]}...")

            return task_data.get("tasks", [])

        except json.JSONDecodeError as e:
            print(f"Error parsing manager response: {e}")
            return []

    def agent_execute_task(self, task: Dict) -> Dict:
        """Have an agent execute their assigned task"""

        agent_id = task["assigned_to"]
        task_id = task["task_id"]

        print(f"\\n[{agent_id}] Working on {task_id}...")

        # Read current communication file for context
        comm_data = self.read_communication_file()

        system_prompt = f"""You are a {agent_id} agent working on a software project.

Your responsibilities:
- Implement assigned tasks following project standards
- Write clean, tested code
- Report blockers clearly and immediately
- Communicate progress through status updates

Project context is in the communication file.
Work diligently and report completion with specific deliverables."""

        prompt = f"""You have been assigned this task:

{json.dumps(task, indent=2)}

Current project state (from team-communication.json):
{json.dumps(comm_data, indent=2)}

Please:
1. Read and understand the task
2. Implement the solution (describe what you would do)
3. Update your status in the communication file

Respond with JSON in this format:
{{
  "status": "completed" or "blocked" or "in_progress",
  "progress": 0-100,
  "message": "What you did",
  "completed_items": ["List of deliverables"],
  "blockers": [],
  "questions_for_manager": []
}}"""

        response = self.call_agent(agent_id, agent_id, prompt, system_prompt)

        # Parse response
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            json_str = response[start:end]
            status_update = json.loads(json_str)

            # Add agent update to communication file
            status_update["timestamp"] = datetime.utcnow().isoformat() + "Z"
            status_update["agent_id"] = agent_id
            status_update["task_id"] = task_id

            comm_data = self.read_communication_file()
            comm_data["agent_updates"].append(status_update)

            # Update task status in manager_instructions
            for t in comm_data["manager_instructions"]["active_tasks"]:
                if t["task_id"] == task_id:
                    t["status"] = status_update["status"]
                    break

            self.write_communication_file(comm_data)

            status = status_update.get("status", "unknown")
            if status == "completed":
                print(f"  [{agent_id}] ✅ Completed {task_id}")
            elif status == "blocked":
                print(f"  [{agent_id}] ⚠️  Blocked on {task_id}")
                if status_update.get("blockers"):
                    for blocker in status_update["blockers"]:
                        print(f"       Blocker: {blocker}")
            else:
                progress = status_update.get("progress", 0)
                print(f"  [{agent_id}] 🔄 Progress: {progress}%")

            return status_update

        except json.JSONDecodeError as e:
            print(f"Error parsing agent response: {e}")
            return {"status": "error", "message": str(e)}

    def manager_resolve_blockers(self):
        """Have manager review blockers and provide resolutions"""

        comm_data = self.read_communication_file()

        # Find agents with blockers
        blocked_updates = [
            update for update in comm_data.get("agent_updates", [])
            if update.get("status") == "blocked" and update.get("blockers")
        ]

        if not blocked_updates:
            return

        print(f"\\n[Manager] Reviewing {len(blocked_updates)} blocker(s)...")

        system_prompt = """You are a Team Manager resolving blockers.

When an agent reports a blocker:
1. Analyze the root cause
2. Provide specific guidance or make a decision
3. Update the communication file with resolution

Be practical and unblock agents quickly."""

        for update in blocked_updates:
            prompt = f"""An agent is blocked:

Agent: {update["agent_id"]}
Task: {update["task_id"]}
Blockers: {json.dumps(update["blockers"], indent=2)}

Current state:
{json.dumps(comm_data, indent=2)}

Please provide a resolution. Respond with JSON:
{{
  "resolution": "Specific guidance",
  "decision": "Decision made (if any)",
  "updated_task": {{updated task object if needed}}
}}"""

            response = self.call_agent("manager", "team_manager", prompt, system_prompt)

            # Parse and apply resolution
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                resolution = json.loads(json_str)

                print(f"  [Manager] Resolution for {update['task_id']}: {resolution.get('resolution', 'N/A')[:80]}...")

                # Add decision to communication file if made
                if resolution.get("decision"):
                    comm_data["manager_instructions"]["decisions"].append({
                        "decision": resolution["decision"],
                        "rationale": resolution["resolution"],
                        "affected_agents": [update["agent_id"]],
                        "in_response_to": f"{update['agent_id']} blocker"
                    })

                    self.write_communication_file(comm_data)

            except json.JSONDecodeError:
                print(f"  [Manager] Could not parse resolution")

    def run(self, feature_description: str, max_iterations: int = 10):
        """
        Run the orchestrator.

        Args:
            feature_description: What to build
            max_iterations: Max coordination loops
        """

        print("=" * 70)
        print("FILE-BASED MULTI-AGENT ORCHESTRATOR")
        print("=" * 70)
        print(f"Project: {self.project_dir}")
        print(f"Communication file: {self.communication_file}")
        print(f"Feature: {feature_description}")
        print("=" * 70)

        # Step 1: Manager creates tasks
        tasks = self.manager_create_tasks(feature_description)

        if not tasks:
            print("\\n❌ Failed to create tasks")
            return {"success": False}

        # Step 2: Execute tasks (simplified sequential for this example)
        for task in tasks:
            # Execute task
            result = self.agent_execute_task(task)

            # If blocked, have manager resolve
            if result.get("status") == "blocked":
                self.manager_resolve_blockers()

                # Retry task after resolution
                result = self.agent_execute_task(task)

        # Step 3: Summary
        comm_data = self.read_communication_file()
        completed_count = sum(
            1 for t in comm_data["manager_instructions"]["active_tasks"]
            if t.get("status") == "completed"
        )

        print("\\n" + "=" * 70)
        print("EXECUTION SUMMARY")
        print("=" * 70)
        print(f"Total tasks: {len(tasks)}")
        print(f"Completed: {completed_count}")
        print(f"Communication file updated: {self.communication_file}")
        print("=" * 70)

        return {
            "success": completed_count == len(tasks),
            "total": len(tasks),
            "completed": completed_count
        }


def main():
    parser = argparse.ArgumentParser(description="File-Based Multi-Agent Orchestrator")
    parser.add_argument("--feature", required=True, help="Feature description")
    parser.add_argument("--project-dir", required=True, help="Project directory")
    parser.add_argument("--api-provider", default="anthropic",
                        choices=["anthropic", "openai"])
    parser.add_argument("--max-iterations", type=int, default=10,
                        help="Max coordination iterations")

    args = parser.parse_args()

    # Validate
    if not Path(args.project_dir).exists():
        print(f"Error: Project directory not found: {args.project_dir}")
        sys.exit(1)

    # Run
    orchestrator = FileBasedOrchestrator(
        project_dir=args.project_dir,
        api_provider=args.api_provider
    )

    result = orchestrator.run(args.feature, args.max_iterations)

    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
