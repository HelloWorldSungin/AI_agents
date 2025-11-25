#!/usr/bin/env python3
"""
Programmatic Tool Calling Orchestrator

Advanced orchestrator that lets Claude write Python code to orchestrate tools,
rather than making sequential tool calls. This reduces context pollution and
eliminates N inference passes for N-tool workflows.

Based on: https://www.anthropic.com/engineering/advanced-tool-use

Key Benefits:
- 37% token reduction on complex tasks
- Eliminates multiple inference passes
- Parallel tool execution via asyncio
- Intermediate results processed in code, only final output returned

Usage:
    python programmatic_orchestrator.py \\
        --feature "user authentication" \\
        --project-dir /path/to/project \\
        --mode programmatic

Requirements:
    - ANTHROPIC_API_KEY environment variable
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# Import sandbox executor
try:
    from sandbox_executor import SandboxExecutor, Tool, ExecutionResult
    HAS_SANDBOX = True
except ImportError:
    HAS_SANDBOX = False

# Import prompt caching
try:
    from prompt_cache import CachedAnthropicClient
    HAS_CACHE = True
except ImportError:
    HAS_CACHE = False


@dataclass
class TaskState:
    """Track state of a task"""
    task_id: str
    description: str
    assigned_to: str
    status: str = "pending"  # pending, in_progress, completed, blocked
    progress: int = 0
    blockers: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    result: Optional[Dict] = None


class ProgrammaticOrchestrator:
    """
    Orchestrator using programmatic tool calling.

    Instead of Claude making individual tool calls and returning results,
    Claude writes Python code that:
    1. Calls multiple tools
    2. Processes intermediate results
    3. Returns only the final aggregated result

    This dramatically reduces context pollution and inference overhead.
    """

    def __init__(
        self,
        project_dir: str,
        enable_cache: bool = True,
        verbose: bool = True
    ):
        self.project_dir = Path(project_dir)
        self.verbose = verbose

        if not HAS_ANTHROPIC:
            raise ImportError("anthropic package required: pip install anthropic")

        if not HAS_SANDBOX:
            raise ImportError("sandbox_executor module required")

        # Initialize API client
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        if enable_cache and HAS_CACHE:
            self.client = CachedAnthropicClient(api_key)
            self.use_cache = True
            if verbose:
                print("  ✓ Prompt caching enabled")
        else:
            self.client = anthropic.Anthropic(api_key=api_key)
            self.use_cache = False

        # Task state
        self.tasks: Dict[str, TaskState] = {}
        self.execution_log: List[Dict] = []

        # Create sandbox with orchestration tools
        self._setup_sandbox()

    def _setup_sandbox(self):
        """Set up sandbox with orchestration tools"""
        tools = [
            Tool(
                name="assign_task",
                func=self._tool_assign_task,
                description="Assign a task to an agent. Args: agent_id (str), task_id (str), description (str)"
            ),
            Tool(
                name="execute_task",
                func=self._tool_execute_task,
                description="Execute a task. Args: task_id (str). Returns: dict with status and result"
            ),
            Tool(
                name="get_task_status",
                func=self._tool_get_task_status,
                description="Get status of a task. Args: task_id (str). Returns: dict with status, progress, blockers"
            ),
            Tool(
                name="get_all_tasks",
                func=self._tool_get_all_tasks,
                description="Get all tasks. Returns: list of task dicts"
            ),
            Tool(
                name="resolve_blocker",
                func=self._tool_resolve_blocker,
                description="Resolve a blocker. Args: task_id (str), resolution (str)"
            ),
            Tool(
                name="aggregate_results",
                func=self._tool_aggregate_results,
                description="Aggregate results from tasks. Args: task_ids (list). Returns: combined results dict"
            ),
            Tool(
                name="parallel_execute",
                func=self._tool_parallel_execute,
                description="Execute multiple tasks in parallel. Args: task_ids (list). Returns: dict of results"
            ),
        ]

        self.sandbox = SandboxExecutor(tools, timeout_seconds=60)

    # =========================================================================
    # Tool implementations
    # =========================================================================

    def _tool_assign_task(self, agent_id: str, task_id: str, description: str) -> Dict:
        """Assign a task to an agent"""
        task = TaskState(
            task_id=task_id,
            description=description,
            assigned_to=agent_id
        )
        self.tasks[task_id] = task

        self._log(f"Assigned {task_id} to {agent_id}")

        return {
            "success": True,
            "task_id": task_id,
            "assigned_to": agent_id
        }

    def _tool_execute_task(self, task_id: str) -> Dict:
        """Execute a task (simulated)"""
        if task_id not in self.tasks:
            return {"success": False, "error": f"Task {task_id} not found"}

        task = self.tasks[task_id]
        task.status = "in_progress"

        # Simulate execution by calling Claude to do the work
        result = self._execute_agent_task(task)

        task.status = result.get("status", "completed")
        task.result = result
        task.deliverables = result.get("deliverables", [])

        self._log(f"Executed {task_id}: {task.status}")

        return {
            "success": True,
            "task_id": task_id,
            "status": task.status,
            "deliverables": task.deliverables,
            "result": result
        }

    def _tool_get_task_status(self, task_id: str) -> Dict:
        """Get task status"""
        if task_id not in self.tasks:
            return {"error": f"Task {task_id} not found"}

        task = self.tasks[task_id]
        return {
            "task_id": task_id,
            "status": task.status,
            "progress": task.progress,
            "blockers": task.blockers,
            "assigned_to": task.assigned_to
        }

    def _tool_get_all_tasks(self) -> List[Dict]:
        """Get all tasks"""
        return [
            {
                "task_id": t.task_id,
                "description": t.description,
                "assigned_to": t.assigned_to,
                "status": t.status,
                "progress": t.progress
            }
            for t in self.tasks.values()
        ]

    def _tool_resolve_blocker(self, task_id: str, resolution: str) -> Dict:
        """Resolve a blocker"""
        if task_id not in self.tasks:
            return {"error": f"Task {task_id} not found"}

        task = self.tasks[task_id]
        task.blockers = []
        task.status = "pending"

        self._log(f"Resolved blocker for {task_id}")

        return {"success": True, "task_id": task_id, "resolution": resolution}

    def _tool_aggregate_results(self, task_ids: List[str]) -> Dict:
        """Aggregate results from multiple tasks"""
        results = {}
        all_deliverables = []

        for task_id in task_ids:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                results[task_id] = {
                    "status": task.status,
                    "deliverables": task.deliverables
                }
                all_deliverables.extend(task.deliverables)

        return {
            "task_count": len(task_ids),
            "completed": sum(1 for t in task_ids if self.tasks.get(t, TaskState("", "", "")).status == "completed"),
            "results": results,
            "all_deliverables": all_deliverables
        }

    def _tool_parallel_execute(self, task_ids: List[str]) -> Dict:
        """Execute multiple tasks (sequentially for now, could be parallelized)"""
        results = {}
        for task_id in task_ids:
            results[task_id] = self._tool_execute_task(task_id)
        return results

    # =========================================================================
    # Agent execution
    # =========================================================================

    def _execute_agent_task(self, task: TaskState) -> Dict:
        """Have an agent execute a task"""
        system_prompt = f"""You are a {task.assigned_to} agent executing a development task.

Analyze the task and provide a response in JSON format with:
- status: "completed" or "blocked"
- deliverables: list of files/items created
- summary: brief description of what was done
- blockers: list of blockers if status is "blocked"

Be concise and practical."""

        prompt = f"""Execute this task:

Task ID: {task.task_id}
Description: {task.description}

Respond with JSON only."""

        try:
            if self.use_cache:
                response, _ = self.client.call_simple(
                    system_prompt=system_prompt,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000
                )
            else:
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2000,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}]
                )
                response = message.content[0].text

            # Parse JSON response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
            return {"status": "completed", "deliverables": [], "summary": response}

        except Exception as e:
            return {"status": "blocked", "blockers": [str(e)], "deliverables": []}

    # =========================================================================
    # Main orchestration
    # =========================================================================

    def _log(self, message: str):
        """Log execution events"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message
        }
        self.execution_log.append(entry)
        if self.verbose:
            print(f"  [{entry['timestamp'][:19]}] {message}")

    def create_orchestration_plan(self, feature_description: str) -> str:
        """
        Have Claude create Python code to orchestrate the feature implementation.

        This is the key difference from traditional orchestration - Claude writes
        code that will be executed in the sandbox, rather than making individual
        tool calls.
        """
        system_prompt = f"""You are an orchestration planner. Your job is to write Python code
that orchestrates a multi-agent development team.

Available tools in the execution environment:
{self.sandbox.get_tool_descriptions()}

Write Python code that:
1. Breaks down the feature into tasks
2. Assigns tasks to appropriate agents (backend-dev, frontend-dev, qa-tester)
3. Executes tasks (can use parallel_execute for independent tasks)
4. Handles any blockers
5. Aggregates final results

Store the final summary in the `result` variable.

IMPORTANT:
- Write pure Python code, no markdown
- Use the tools provided
- Process intermediate results in code - only the final `result` is returned
- Be practical and concise"""

        prompt = f"""Create an orchestration plan for this feature:

{feature_description}

Write Python code that orchestrates the implementation using the available tools.
The code will be executed in a sandbox with only these tools available.

Remember: Store your final summary in `result`."""

        try:
            if self.use_cache:
                response, cache_info = self.client.call_simple(
                    system_prompt=system_prompt,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=4000
                )
                if self.verbose and cache_info.get("cache_read_input_tokens", 0) > 0:
                    print(f"  [Cache] Hit! Saved {cache_info['cache_read_input_tokens']} tokens")
            else:
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4000,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}]
                )
                response = message.content[0].text

            # Extract code from response
            code = self._extract_code(response)
            return code

        except Exception as e:
            raise RuntimeError(f"Failed to create orchestration plan: {e}")

    def _extract_code(self, response: str) -> str:
        """Extract Python code from Claude's response"""
        # Try to find code block
        if "```python" in response:
            start = response.find("```python") + 9
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()

        if "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()

        # Assume entire response is code
        return response.strip()

    def run(self, feature_description: str) -> Dict:
        """
        Run programmatic orchestration for a feature.

        This:
        1. Has Claude generate orchestration code
        2. Executes the code in the sandbox
        3. Returns the final result (not intermediate tool outputs)
        """
        print("=" * 70)
        print("PROGRAMMATIC TOOL CALLING ORCHESTRATOR")
        print("=" * 70)
        print(f"Project: {self.project_dir}")
        print(f"Feature: {feature_description}")
        print(f"Mode: Programmatic (code-based orchestration)")
        print("=" * 70)

        # Step 1: Generate orchestration code
        print("\n[Planner] Generating orchestration code...")
        code = self.create_orchestration_plan(feature_description)

        if self.verbose:
            print("\n[Generated Code]")
            print("-" * 40)
            for i, line in enumerate(code.split('\n'), 1):
                print(f"{i:3}: {line}")
            print("-" * 40)

        # Step 2: Execute in sandbox
        print("\n[Executor] Running orchestration code...")
        result = self.sandbox.execute(code)

        # Step 3: Report results
        print("\n" + "=" * 70)
        print("EXECUTION SUMMARY")
        print("=" * 70)
        print(f"Success: {result.success}")
        print(f"Execution time: {result.execution_time_ms:.2f}ms")
        print(f"Tool calls made: {len(result.tool_calls)}")

        if result.output:
            print(f"\nOutput:")
            print(result.output[:500])

        if result.error:
            print(f"\nError: {result.error}")

        if result.result:
            print(f"\nFinal Result:")
            print(json.dumps(result.result, indent=2)[:1000])

        # Show stats
        if self.use_cache and hasattr(self.client, 'get_stats'):
            stats = self.client.get_stats()
            print("\n" + "-" * 35)
            print("CACHE STATISTICS")
            print("-" * 35)
            print(f"API calls: {stats['total_calls']}")
            print(f"Cache hit rate: {stats['hit_rate']}")
            print(f"Tokens saved: {stats['tokens_saved']}")

        print("=" * 70)

        return {
            "success": result.success,
            "result": result.result,
            "tool_calls": len(result.tool_calls),
            "execution_time_ms": result.execution_time_ms,
            "tasks": self._tool_get_all_tasks()
        }


def compare_modes(feature: str, project_dir: str):
    """Compare programmatic vs sequential orchestration"""
    print("\n" + "=" * 70)
    print("MODE COMPARISON")
    print("=" * 70)

    # Programmatic mode
    print("\n[1] PROGRAMMATIC MODE")
    prog_orch = ProgrammaticOrchestrator(project_dir, verbose=False)
    prog_result = prog_orch.run(feature)

    print(f"\nProgrammatic Results:")
    print(f"  - Success: {prog_result['success']}")
    print(f"  - Tool calls: {prog_result['tool_calls']}")
    print(f"  - Execution time: {prog_result['execution_time_ms']:.2f}ms")

    # Note: Sequential mode comparison would require running the
    # simple_orchestrator for the same feature

    print("\n" + "-" * 35)
    print("BENEFITS OF PROGRAMMATIC MODE:")
    print("-" * 35)
    print("• Intermediate results stay in code (not returned to model)")
    print("• Single inference pass generates all orchestration logic")
    print("• Parallel execution possible via asyncio")
    print("• ~37% token reduction on complex workflows")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Programmatic Tool Calling Orchestrator"
    )
    parser.add_argument("--feature", required=True, help="Feature to implement")
    parser.add_argument("--project-dir", required=True, help="Project directory")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--compare", action="store_true",
                        help="Compare programmatic vs sequential modes")
    parser.add_argument("--no-cache", action="store_true",
                        help="Disable prompt caching")

    args = parser.parse_args()

    if not Path(args.project_dir).exists():
        print(f"Error: Project directory not found: {args.project_dir}")
        sys.exit(1)

    if args.compare:
        compare_modes(args.feature, args.project_dir)
    else:
        orchestrator = ProgrammaticOrchestrator(
            project_dir=args.project_dir,
            enable_cache=not args.no_cache,
            verbose=args.verbose
        )
        result = orchestrator.run(args.feature)
        sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
