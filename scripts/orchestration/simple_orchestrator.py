#!/usr/bin/env python3
"""
Simple Multi-Agent Orchestrator

A basic example of automated multi-agent coordination using LLM APIs.
This script demonstrates:
- Manager agent creating task breakdowns
- Task agents executing work
- Basic blocker handling
- Sequential coordination

Usage:
    python simple_orchestrator.py --feature "user authentication" --project-dir /path/to/project

Requirements:
    - ANTHROPIC_API_KEY environment variable
    - Or OPENAI_API_KEY environment variable
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Try to import Anthropic or OpenAI
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
    print("Error: Please install either 'anthropic' or 'openai' package")
    print("  pip install anthropic")
    print("  or")
    print("  pip install openai")
    sys.exit(1)


@dataclass
class Task:
    """Represents a task for an agent"""
    task_id: str
    description: str
    assigned_to: str
    status: str = "not_started"  # not_started, in_progress, blocked, completed
    blockers: List[str] = field(default_factory=list)
    result: Optional[str] = None


@dataclass
class Agent:
    """Represents an AI agent"""
    agent_id: str
    role: str
    prompt_file: str
    model: str = "claude-sonnet-4"


class SimpleOrchestrator:
    """
    Simple orchestrator for multi-agent coordination.

    This is a basic implementation that demonstrates the core concepts
    without requiring complex infrastructure.
    """

    def __init__(self, project_dir: str, api_provider: str = "anthropic"):
        self.project_dir = Path(project_dir)
        self.api_provider = api_provider

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

        # State
        self.tasks: List[Task] = []
        self.conversation_history: Dict[str, List] = {}

    def load_agent_prompt(self, prompt_file: str) -> str:
        """Load agent prompt from library"""
        prompt_path = self.project_dir / ".ai-agents" / "library" / prompt_file

        if not prompt_path.exists():
            # Fallback to simple prompts
            return self._get_default_prompt(prompt_file)

        with open(prompt_path, 'r') as f:
            return f.read()

    def _get_default_prompt(self, role: str) -> str:
        """Get default prompt for role"""
        if "manager" in role:
            return """You are a Team Manager for a software development team.

Your responsibilities:
- Break down features into tasks
- Assign tasks to appropriate agents (backend-dev, frontend-dev, qa-tester)
- Coordinate between agents
- Resolve blockers
- Make architectural decisions

When given a feature request, create a task breakdown in this JSON format:
{
  "tasks": [
    {
      "task_id": "TASK-001",
      "description": "Clear description",
      "assigned_to": "backend-dev",
      "dependencies": []
    }
  ]
}

Be practical and specific."""

        elif "backend" in role or "frontend" in role:
            return f"""You are a Software Developer ({role}).

Your responsibilities:
- Implement assigned tasks
- Write clean, tested code
- Report blockers clearly
- Communicate progress

When working on a task:
1. Analyze the requirements
2. Implement the solution
3. Report completion with summary

If blocked, clearly state:
- What you're blocked on
- What you need to proceed
- Suggested workaround (if any)"""

        elif "qa" in role:
            return """You are a QA Tester.

Your responsibilities:
- Write comprehensive tests
- Verify implementations
- Report bugs clearly
- Ensure quality standards

When testing:
1. Review implementation
2. Write appropriate tests (unit, integration, E2E)
3. Run tests and report results"""

        else:
            return f"You are a {role} agent. Help accomplish the assigned task."

    def call_agent(self, agent: Agent, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call an agent via LLM API"""

        # Initialize conversation history if needed
        if agent.agent_id not in self.conversation_history:
            self.conversation_history[agent.agent_id] = []

        # Add user message
        self.conversation_history[agent.agent_id].append({
            "role": "user",
            "content": prompt
        })

        # Call API
        if self.api_provider == "anthropic":
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                system=system_prompt or self.load_agent_prompt(agent.prompt_file),
                messages=self.conversation_history[agent.agent_id]
            )
            response = message.content[0].text

        elif self.api_provider == "openai":
            messages = [{"role": "system", "content": system_prompt or self.load_agent_prompt(agent.prompt_file)}]
            messages.extend(self.conversation_history[agent.agent_id])

            completion = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages
            )
            response = completion.choices[0].message.content

        # Add assistant response to history
        self.conversation_history[agent.agent_id].append({
            "role": "assistant",
            "content": response
        })

        return response

    def create_task_breakdown(self, feature_description: str) -> List[Task]:
        """Have manager create task breakdown"""

        print(f"\n[Manager] Creating task breakdown for: {feature_description}")

        manager = Agent(
            agent_id="manager",
            role="team_manager",
            prompt_file="base/manager.md"
        )

        prompt = f"""Please create a task breakdown for this feature:

{feature_description}

Available agents:
- backend-dev: Backend development
- frontend-dev: Frontend development
- qa-tester: Testing and quality assurance

Create a practical task breakdown with 3-5 tasks. Return ONLY valid JSON in the format:
{{
  "tasks": [
    {{
      "task_id": "TASK-001",
      "description": "Specific task description",
      "assigned_to": "backend-dev|frontend-dev|qa-tester",
      "dependencies": []
    }}
  ]
}}"""

        response = self.call_agent(manager, prompt)

        # Extract JSON from response
        try:
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            json_str = response[start:end]

            task_data = json.loads(json_str)

            tasks = []
            for t in task_data["tasks"]:
                task = Task(
                    task_id=t["task_id"],
                    description=t["description"],
                    assigned_to=t["assigned_to"]
                )
                tasks.append(task)
                print(f"  [Manager] Created {task.task_id}: {task.description[:50]}... → {task.assigned_to}")

            return tasks

        except json.JSONDecodeError as e:
            print(f"Error parsing manager response: {e}")
            print(f"Response was: {response}")
            return []

    def execute_task(self, task: Task) -> str:
        """Have an agent execute a task"""

        print(f"\n[{task.assigned_to}] Working on {task.task_id}: {task.description[:50]}...")

        agent = Agent(
            agent_id=task.assigned_to,
            role=task.assigned_to,
            prompt_file=f"base/software-developer.md"
        )

        prompt = f"""You have been assigned this task:

Task ID: {task.task_id}
Description: {task.description}

Project directory: {self.project_dir}

Please:
1. Analyze what needs to be done
2. Implement the solution (describe the changes you would make)
3. Report completion

If you encounter any blockers, clearly state what you need.

Provide your response in this format:
STATUS: [completed|blocked]
SUMMARY: Brief summary of what you did
BLOCKERS: List any blockers (or "None")
FILES_MODIFIED: List files you would create/modify"""

        response = self.call_agent(agent, prompt)

        # Parse response
        if "STATUS: blocked" in response or "STATUS:blocked" in response:
            task.status = "blocked"
            # Extract blocker
            if "BLOCKERS:" in response:
                blocker_start = response.find("BLOCKERS:") + len("BLOCKERS:")
                blocker_end = response.find("\n", blocker_start)
                blocker = response[blocker_start:blocker_end].strip()
                task.blockers.append(blocker)
                print(f"  [{task.assigned_to}] ⚠️  BLOCKED: {blocker}")
        else:
            task.status = "completed"
            print(f"  [{task.assigned_to}] ✅ Completed {task.task_id}")

        task.result = response
        return response

    def resolve_blocker(self, task: Task) -> bool:
        """Have manager try to resolve a blocker"""

        print(f"\n[Manager] Attempting to resolve blocker for {task.task_id}")

        manager = Agent(
            agent_id="manager",
            role="team_manager",
            prompt_file="base/manager.md"
        )

        prompt = f"""An agent is blocked:

Task: {task.description}
Agent: {task.assigned_to}
Blocker: {task.blockers[0] if task.blockers else 'Unknown'}

Please provide guidance or a decision to unblock this agent.
Be specific and actionable."""

        response = self.call_agent(manager, prompt)

        print(f"  [Manager] Resolution: {response[:100]}...")

        # For now, assume blocker is resolved
        # In a real system, you'd update shared state and retry
        return True

    def run(self, feature_description: str) -> Dict:
        """
        Run the orchestrator for a feature.

        Returns summary of execution.
        """

        print("=" * 70)
        print("SIMPLE MULTI-AGENT ORCHESTRATOR")
        print("=" * 70)
        print(f"Project: {self.project_dir}")
        print(f"Feature: {feature_description}")
        print(f"API Provider: {self.api_provider}")
        print("=" * 70)

        # Step 1: Get task breakdown from manager
        tasks = self.create_task_breakdown(feature_description)

        if not tasks:
            print("\n❌ Failed to create task breakdown")
            return {"success": False, "error": "No tasks created"}

        self.tasks = tasks

        # Step 2: Execute tasks sequentially
        completed = 0
        blocked = 0

        for task in self.tasks:
            self.execute_task(task)

            if task.status == "blocked":
                blocked += 1
                # Try to resolve
                if self.resolve_blocker(task):
                    # Retry task
                    self.execute_task(task)
                    if task.status == "completed":
                        completed += 1
                        blocked -= 1
            elif task.status == "completed":
                completed += 1

        # Step 3: Summary
        print("\n" + "=" * 70)
        print("EXECUTION SUMMARY")
        print("=" * 70)
        print(f"Total tasks: {len(self.tasks)}")
        print(f"Completed: {completed}")
        print(f"Blocked: {blocked}")
        print("=" * 70)

        return {
            "success": completed == len(self.tasks),
            "total_tasks": len(self.tasks),
            "completed": completed,
            "blocked": blocked,
            "tasks": [
                {
                    "task_id": t.task_id,
                    "description": t.description,
                    "assigned_to": t.assigned_to,
                    "status": t.status
                }
                for t in self.tasks
            ]
        }


def main():
    parser = argparse.ArgumentParser(description="Simple Multi-Agent Orchestrator")
    parser.add_argument("--feature", required=True, help="Feature description")
    parser.add_argument("--project-dir", required=True, help="Project directory path")
    parser.add_argument("--api-provider", default="anthropic", choices=["anthropic", "openai"],
                        help="API provider to use")

    args = parser.parse_args()

    # Validate project directory
    project_path = Path(args.project_dir)
    if not project_path.exists():
        print(f"Error: Project directory does not exist: {project_path}")
        sys.exit(1)

    # Create orchestrator
    orchestrator = SimpleOrchestrator(
        project_dir=str(project_path),
        api_provider=args.api_provider
    )

    # Run
    result = orchestrator.run(args.feature)

    # Exit with appropriate code
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
