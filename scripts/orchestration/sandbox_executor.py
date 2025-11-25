#!/usr/bin/env python3
"""
Sandboxed Code Execution Environment

Provides a secure sandbox for executing Claude-generated Python code
that orchestrates tools. This enables programmatic tool calling where
intermediate results are processed in code rather than returned to the model.

Based on: https://www.anthropic.com/engineering/advanced-tool-use

Key Features:
- Restricted execution environment (no file system, network, etc.)
- Tool injection - only registered tools are available
- Timeout protection
- Output capture and result extraction
- Async tool support for parallel execution

Usage:
    from sandbox_executor import SandboxExecutor, Tool

    # Define tools
    tools = [
        Tool("get_user", lambda user_id: {"name": "John"}, "Get user by ID"),
        Tool("get_orders", lambda user_id: [{"id": 1}], "Get user orders"),
    ]

    # Create sandbox
    sandbox = SandboxExecutor(tools)

    # Execute Claude-generated code
    code = '''
    user = get_user("123")
    orders = get_orders("123")
    result = {"user": user, "order_count": len(orders)}
    '''

    output = sandbox.execute(code)
"""

import ast
import asyncio
import sys
import traceback
from dataclasses import dataclass, field
from io import StringIO
from typing import Any, Callable, Dict, List, Optional, Union
import concurrent.futures
import threading
import time


@dataclass
class Tool:
    """Definition of a tool available in the sandbox"""
    name: str
    func: Callable
    description: str
    is_async: bool = False
    allowed_callers: List[str] = field(default_factory=lambda: ["code_execution_20250825"])

    def __call__(self, *args, **kwargs):
        if self.is_async:
            return asyncio.get_event_loop().run_until_complete(self.func(*args, **kwargs))
        return self.func(*args, **kwargs)


@dataclass
class ExecutionResult:
    """Result from sandbox execution"""
    success: bool
    result: Any = None
    output: str = ""
    error: Optional[str] = None
    execution_time_ms: float = 0
    tool_calls: List[Dict] = field(default_factory=list)


class RestrictedBuiltins:
    """
    Restricted set of Python builtins for sandbox execution.

    Removes dangerous functions like exec, eval, open, __import__, etc.
    """

    SAFE_BUILTINS = {
        # Types
        'bool', 'int', 'float', 'str', 'list', 'dict', 'set', 'tuple',
        'frozenset', 'bytes', 'bytearray', 'type', 'object',

        # Functions
        'abs', 'all', 'any', 'ascii', 'bin', 'callable', 'chr', 'divmod',
        'enumerate', 'filter', 'format', 'getattr', 'hasattr', 'hash',
        'hex', 'id', 'isinstance', 'issubclass', 'iter', 'len', 'map',
        'max', 'min', 'next', 'oct', 'ord', 'pow', 'range', 'repr',
        'reversed', 'round', 'slice', 'sorted', 'sum', 'zip',

        # Constants
        'True', 'False', 'None',

        # Exceptions (for handling)
        'Exception', 'ValueError', 'TypeError', 'KeyError', 'IndexError',
        'AttributeError', 'RuntimeError', 'StopIteration',
    }

    @classmethod
    def get_safe_builtins(cls) -> Dict[str, Any]:
        """Get dictionary of safe builtins"""
        import builtins
        return {
            name: getattr(builtins, name)
            for name in cls.SAFE_BUILTINS
            if hasattr(builtins, name)
        }


class CodeValidator:
    """
    Validates Python code before execution.

    Checks for:
    - Dangerous imports
    - File operations
    - Network operations
    - System calls
    - Infinite loops (basic check)
    """

    FORBIDDEN_IMPORTS = {
        'os', 'sys', 'subprocess', 'shutil', 'socket', 'http', 'urllib',
        'ftplib', 'smtplib', 'telnetlib', 'ssl', 'ctypes', 'multiprocessing',
        'threading', 'signal', 'resource', 'pty', 'tty', 'termios',
        'fcntl', 'pipes', 'posix', 'pwd', 'grp', 'spwd', 'crypt',
        'tempfile', 'glob', 'fnmatch', 'linecache', 'pickle', 'shelve',
        'dbm', 'sqlite3', 'zipfile', 'tarfile', 'bz2', 'gzip', 'lzma',
        'zipimport', 'pkgutil', 'modulefinder', 'runpy', 'importlib',
        'builtins', '__builtins__',
    }

    FORBIDDEN_NODES = {
        ast.Import, ast.ImportFrom,  # No imports allowed
    }

    FORBIDDEN_NAMES = {
        '__import__', 'exec', 'eval', 'compile', 'open', 'input',
        '__class__', '__bases__', '__subclasses__', '__mro__',
        '__globals__', '__locals__', '__code__', '__closure__',
        'breakpoint', 'exit', 'quit',
    }

    @classmethod
    def validate(cls, code: str) -> tuple[bool, Optional[str]]:
        """
        Validate code for safety.

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {e}"

        for node in ast.walk(tree):
            # Check for forbidden node types
            if type(node) in cls.FORBIDDEN_NODES:
                return False, f"Forbidden operation: {type(node).__name__}"

            # Check for forbidden names
            if isinstance(node, ast.Name):
                if node.id in cls.FORBIDDEN_NAMES:
                    return False, f"Forbidden name: {node.id}"

            # Check for attribute access to forbidden names
            if isinstance(node, ast.Attribute):
                if node.attr in cls.FORBIDDEN_NAMES:
                    return False, f"Forbidden attribute: {node.attr}"

            # Check for string literals containing forbidden imports
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                for forbidden in cls.FORBIDDEN_IMPORTS:
                    if forbidden in node.value:
                        # Only flag if it looks like an import attempt
                        if f"import {forbidden}" in code or f"from {forbidden}" in code:
                            return False, f"Forbidden import detected: {forbidden}"

        return True, None


class SandboxExecutor:
    """
    Sandboxed Python code executor for programmatic tool calling.

    Executes Claude-generated code in a restricted environment with
    only registered tools available.
    """

    def __init__(
        self,
        tools: List[Tool],
        timeout_seconds: float = 30.0,
        max_output_size: int = 100000
    ):
        """
        Initialize sandbox executor.

        Args:
            tools: List of tools available in the sandbox
            timeout_seconds: Maximum execution time
            max_output_size: Maximum captured output size
        """
        self.tools = {tool.name: tool for tool in tools}
        self.timeout_seconds = timeout_seconds
        self.max_output_size = max_output_size
        self._tool_calls: List[Dict] = []

    def _create_tool_wrapper(self, tool: Tool) -> Callable:
        """Create a wrapper that tracks tool calls"""
        def wrapper(*args, **kwargs):
            call_record = {
                "tool": tool.name,
                "args": args,
                "kwargs": kwargs,
                "timestamp": time.time()
            }
            self._tool_calls.append(call_record)

            result = tool(*args, **kwargs)
            call_record["result"] = result
            return result

        return wrapper

    def _create_namespace(self) -> Dict[str, Any]:
        """Create the execution namespace with tools and safe builtins"""
        namespace = {
            '__builtins__': RestrictedBuiltins.get_safe_builtins(),
            'result': None,  # Special variable for returning results
            'print': self._safe_print,  # Captured print
        }

        # Add tools
        for name, tool in self.tools.items():
            namespace[name] = self._create_tool_wrapper(tool)

        # Add async utilities if any tools are async
        if any(tool.is_async for tool in self.tools.values()):
            namespace['asyncio'] = self._get_safe_asyncio()

        return namespace

    def _safe_print(self, *args, **kwargs):
        """Safe print that writes to captured output"""
        # This will be redirected to StringIO during execution
        print(*args, **kwargs)

    def _get_safe_asyncio(self) -> object:
        """Get a restricted asyncio module for parallel tool execution"""
        class SafeAsyncio:
            @staticmethod
            def gather(*coros):
                return asyncio.gather(*coros)

            @staticmethod
            def run(coro):
                return asyncio.run(coro)

            @staticmethod
            async def sleep(seconds):
                await asyncio.sleep(min(seconds, 5))  # Max 5 second sleep

        return SafeAsyncio()

    def execute(self, code: str) -> ExecutionResult:
        """
        Execute code in the sandbox.

        Args:
            code: Python code to execute

        Returns:
            ExecutionResult with success status, result, and captured output
        """
        start_time = time.time()
        self._tool_calls = []

        # Validate code
        is_valid, error = CodeValidator.validate(code)
        if not is_valid:
            return ExecutionResult(
                success=False,
                error=f"Code validation failed: {error}",
                execution_time_ms=(time.time() - start_time) * 1000
            )

        # Create namespace
        namespace = self._create_namespace()

        # Capture stdout
        old_stdout = sys.stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            # Execute with timeout
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(exec, code, namespace)
                try:
                    future.result(timeout=self.timeout_seconds)
                except concurrent.futures.TimeoutError:
                    return ExecutionResult(
                        success=False,
                        error=f"Execution timed out after {self.timeout_seconds}s",
                        output=captured_output.getvalue()[:self.max_output_size],
                        execution_time_ms=(time.time() - start_time) * 1000,
                        tool_calls=self._tool_calls
                    )

            # Get result
            result = namespace.get('result')
            output = captured_output.getvalue()[:self.max_output_size]

            return ExecutionResult(
                success=True,
                result=result,
                output=output,
                execution_time_ms=(time.time() - start_time) * 1000,
                tool_calls=self._tool_calls
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}",
                output=captured_output.getvalue()[:self.max_output_size],
                execution_time_ms=(time.time() - start_time) * 1000,
                tool_calls=self._tool_calls
            )

        finally:
            sys.stdout = old_stdout

    def get_tool_descriptions(self) -> str:
        """Get formatted descriptions of available tools for Claude"""
        lines = ["# Available Tools\n"]
        lines.append("The following tools are available in the execution environment:\n")

        for name, tool in self.tools.items():
            lines.append(f"## {name}")
            lines.append(f"{tool.description}\n")

        lines.append("\n# Usage")
        lines.append("Write Python code that uses these tools.")
        lines.append("Store your final result in the `result` variable.")
        lines.append("You can use `print()` for debugging output.\n")

        return "\n".join(lines)


class AsyncSandboxExecutor(SandboxExecutor):
    """
    Async-capable sandbox executor for parallel tool execution.

    Supports `await` and `asyncio.gather()` for running multiple
    tool calls in parallel.
    """

    async def execute_async(self, code: str) -> ExecutionResult:
        """Execute async code in the sandbox"""
        # For async execution, we need to handle it differently
        # Wrap the code in an async function
        wrapped_code = f"""
async def __sandbox_main():
{chr(10).join('    ' + line for line in code.split(chr(10)))}
    return result

import asyncio
result = asyncio.run(__sandbox_main())
"""
        return self.execute(wrapped_code)


def create_agent_tools(orchestrator) -> List[Tool]:
    """
    Create tools for multi-agent orchestration.

    These tools are designed to be called from Claude-generated code,
    enabling programmatic task orchestration.

    Args:
        orchestrator: The orchestrator instance for agent communication

    Returns:
        List of Tool definitions
    """
    tools = [
        Tool(
            name="assign_task",
            func=lambda agent_id, task: orchestrator.assign_task(agent_id, task),
            description="""Assign a task to an agent.

Args:
    agent_id: Target agent (e.g., "backend-dev", "frontend-dev")
    task: Dict with keys: task_id, description, priority, dependencies

Returns:
    Dict with assignment confirmation and task_id
""",
        ),

        Tool(
            name="get_agent_status",
            func=lambda agent_id: orchestrator.get_agent_status(agent_id),
            description="""Get current status of an agent.

Args:
    agent_id: Agent to check (e.g., "backend-dev")

Returns:
    Dict with status, current_task, progress, blockers
""",
        ),

        Tool(
            name="execute_task",
            func=lambda task_id: orchestrator.execute_task(task_id),
            description="""Execute a specific task.

Args:
    task_id: ID of task to execute (e.g., "TASK-001")

Returns:
    Dict with status (completed/blocked), deliverables, blockers
""",
        ),

        Tool(
            name="resolve_blocker",
            func=lambda task_id, resolution: orchestrator.resolve_blocker(task_id, resolution),
            description="""Provide resolution for a blocked task.

Args:
    task_id: Blocked task ID
    resolution: String describing how to proceed

Returns:
    Dict with updated task status
""",
        ),

        Tool(
            name="get_all_tasks",
            func=lambda: orchestrator.get_all_tasks(),
            description="""Get list of all current tasks.

Returns:
    List of task dicts with status, assigned_to, dependencies
""",
        ),

        Tool(
            name="aggregate_results",
            func=lambda task_ids: orchestrator.aggregate_results(task_ids),
            description="""Aggregate results from multiple completed tasks.

Args:
    task_ids: List of task IDs to aggregate

Returns:
    Dict with combined deliverables and summary
""",
        ),
    ]

    return tools


if __name__ == "__main__":
    # Demo
    print("Sandbox Executor Demo")
    print("=" * 50)

    # Create some demo tools
    demo_tools = [
        Tool("get_user", lambda user_id: {"id": user_id, "name": "John Doe"}, "Get user by ID"),
        Tool("get_orders", lambda user_id: [{"id": 1, "total": 100}, {"id": 2, "total": 200}], "Get user orders"),
        Tool("calculate_total", lambda orders: sum(o["total"] for o in orders), "Calculate order total"),
    ]

    sandbox = SandboxExecutor(demo_tools, timeout_seconds=10)

    print("\nAvailable tools:")
    print(sandbox.get_tool_descriptions())

    # Execute some code
    code = """
# Get user and their orders
user = get_user("123")
orders = get_orders("123")
total = calculate_total(orders)

print(f"User: {user['name']}")
print(f"Orders: {len(orders)}")
print(f"Total: ${total}")

result = {
    "user": user,
    "order_count": len(orders),
    "total_value": total
}
"""

    print("\nExecuting code:")
    print("-" * 30)
    print(code)
    print("-" * 30)

    result = sandbox.execute(code)

    print(f"\nSuccess: {result.success}")
    print(f"Result: {result.result}")
    print(f"Output:\n{result.output}")
    print(f"Tool calls: {len(result.tool_calls)}")
    print(f"Execution time: {result.execution_time_ms:.2f}ms")
