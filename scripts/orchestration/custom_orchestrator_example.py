#!/usr/bin/env python3
"""
Custom Orchestrator Example

This shows how to create a custom orchestrator with your own logic.
Useful for specific workflows or project needs.
"""

import os
import json
from pathlib import Path
from typing import List, Dict
import anthropic


class CustomOrchestrator:
    """
    Example custom orchestrator with specific workflow.

    This one implements a "Design-First" workflow:
    1. Architect designs the system
    2. Manager creates technical specs
    3. Developers implement in parallel
    4. QA validates everything
    """

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )
        self.comm_file = self.project_dir / ".ai-agents/state/team-communication.json"

    def call_agent(self, role: str, prompt: str, system: str) -> str:
        """Call an agent via Anthropic API"""
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            system=system,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def phase_1_architect_design(self, feature: str) -> Dict:
        """Phase 1: Architect creates high-level design"""
        print("\n=== PHASE 1: ARCHITECTURAL DESIGN ===\n")

        system = """You are a Software Architect.

Create high-level system design for features.

Output:
- Component breakdown
- Data models
- API contracts
- Integration points

Be thorough but concise."""

        prompt = f"""Design the architecture for this feature:

{feature}

Create a comprehensive design document covering:
1. Component breakdown
2. Data models
3. API contracts
4. Integration approach

Return as JSON with these sections."""

        response = self.call_agent("architect", prompt, system)

        # Parse design
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            design = json.loads(response[start:end])

            print("✅ Architecture designed")
            print(f"   Components: {len(design.get('components', []))}")
            print(f"   Data models: {len(design.get('data_models', []))}")

            return design
        except json.JSONDecodeError:
            print("⚠️  Could not parse design, using text format")
            return {"design_text": response}

    def phase_2_manager_planning(self, design: Dict) -> List[Dict]:
        """Phase 2: Manager creates detailed task plan"""
        print("\n=== PHASE 2: TASK PLANNING ===\n")

        system = """You are a Team Manager.

Given an architectural design, create detailed implementation tasks.

Break work into:
- Backend tasks (API, database, services)
- Frontend tasks (UI, state, integration)
- Testing tasks (unit, integration, E2E)

Each task should be specific and actionable."""

        prompt = f"""Based on this architectural design:

{json.dumps(design, indent=2)}

Create detailed implementation tasks.

Return as JSON:
{{
  "tasks": [
    {{
      "task_id": "TASK-001",
      "description": "Specific task",
      "assigned_to": "backend-dev|frontend-dev|qa-tester",
      "estimated_hours": 4,
      "dependencies": []
    }}
  ]
}}"""

        response = self.call_agent("manager", prompt, system)

        # Parse tasks
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            plan = json.loads(response[start:end])

            tasks = plan.get("tasks", [])
            print(f"✅ Created {len(tasks)} tasks")
            for task in tasks:
                print(f"   {task['task_id']}: {task['description'][:50]}...")

            # Write to communication file
            comm_data = self._read_comm_file()
            comm_data["manager_instructions"]["active_tasks"] = tasks
            self._write_comm_file(comm_data)

            return tasks
        except json.JSONDecodeError:
            print("⚠️  Could not parse tasks")
            return []

    def phase_3_parallel_implementation(self, tasks: List[Dict]) -> List[Dict]:
        """Phase 3: Developers implement in parallel"""
        print("\n=== PHASE 3: PARALLEL IMPLEMENTATION ===\n")

        # Group tasks by agent
        backend_tasks = [t for t in tasks if t["assigned_to"] == "backend-dev"]
        frontend_tasks = [t for t in tasks if t["assigned_to"] == "frontend-dev"]

        results = []

        # Backend implementation
        if backend_tasks:
            print(f"Backend working on {len(backend_tasks)} tasks...")
            for task in backend_tasks:
                result = self._execute_task("backend-dev", task)
                results.append(result)

        # Frontend implementation (can run parallel in production)
        if frontend_tasks:
            print(f"Frontend working on {len(frontend_tasks)} tasks...")
            for task in frontend_tasks:
                result = self._execute_task("frontend-dev", task)
                results.append(result)

        return results

    def phase_4_qa_validation(self, tasks: List[Dict]) -> Dict:
        """Phase 4: QA validates everything"""
        print("\n=== PHASE 4: QA VALIDATION ===\n")

        system = """You are a QA Tester.

Validate all implementations comprehensively.

Test:
- Unit tests
- Integration tests
- E2E tests
- Edge cases
- Error handling

Report results clearly."""

        # Get all completed work
        comm_data = self._read_comm_file()

        prompt = f"""Review and test all completed work:

{json.dumps(comm_data, indent=2)}

Write comprehensive tests and report results.

Return as JSON:
{{
  "test_suites": [
    {{
      "name": "Unit Tests",
      "passed": 24,
      "failed": 0,
      "coverage": 95
    }}
  ],
  "issues_found": [],
  "overall_status": "pass|fail"
}}"""

        response = self.call_agent("qa-tester", prompt, system)

        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            results = json.loads(response[start:end])

            print("✅ QA validation complete")
            for suite in results.get("test_suites", []):
                print(f"   {suite['name']}: {suite['passed']} passed, {suite['failed']} failed")

            return results
        except json.JSONDecodeError:
            return {"overall_status": "unknown"}

    def _execute_task(self, agent_id: str, task: Dict) -> Dict:
        """Execute a single task"""
        system = f"""You are a {agent_id} working on a software project.

Implement the assigned task following best practices.
Write clean, tested code.
Report completion with specific deliverables."""

        prompt = f"""Implement this task:

{json.dumps(task, indent=2)}

Project context: {self.project_dir}

Provide detailed implementation summary."""

        response = self.call_agent(agent_id, prompt, system)

        print(f"  ✅ {task['task_id']} completed by {agent_id}")

        # Update communication file
        comm_data = self._read_comm_file()
        comm_data["agent_updates"].append({
            "agent_id": agent_id,
            "task_id": task["task_id"],
            "status": "completed",
            "summary": response[:200]
        })
        self._write_comm_file(comm_data)

        return {"task_id": task["task_id"], "status": "completed"}

    def _read_comm_file(self) -> Dict:
        """Read communication file"""
        if not self.comm_file.exists():
            return {
                "manager_instructions": {"active_tasks": []},
                "agent_updates": []
            }
        with open(self.comm_file, 'r') as f:
            return json.load(f)

    def _write_comm_file(self, data: Dict):
        """Write communication file"""
        self.comm_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.comm_file, 'w') as f:
            json.dump(data, f, indent=2)

    def run(self, feature: str):
        """Run the custom workflow"""
        print("="*70)
        print("CUSTOM DESIGN-FIRST ORCHESTRATOR")
        print("="*70)
        print(f"Feature: {feature}")
        print("="*70)

        # Phase 1: Architecture
        design = self.phase_1_architect_design(feature)

        # Phase 2: Planning
        tasks = self.phase_2_manager_planning(design)

        if not tasks:
            print("\n❌ No tasks created, exiting")
            return

        # Phase 3: Implementation
        results = self.phase_3_parallel_implementation(tasks)

        # Phase 4: QA
        qa_results = self.phase_4_qa_validation(tasks)

        # Summary
        print("\n" + "="*70)
        print("WORKFLOW COMPLETE")
        print("="*70)
        print(f"Design: ✅")
        print(f"Tasks: {len(tasks)}")
        print(f"Completed: {len(results)}")
        print(f"QA Status: {qa_results.get('overall_status', 'unknown')}")
        print("="*70)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python custom_orchestrator_example.py <project_dir> <feature>")
        sys.exit(1)

    project_dir = sys.argv[1]
    feature = sys.argv[2]

    orchestrator = CustomOrchestrator(project_dir)
    orchestrator.run(feature)
