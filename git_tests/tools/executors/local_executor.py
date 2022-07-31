import abc
import subprocess

import pexpect

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, AnyStr


@dataclass
class LocalExecutionResult:
    """Result structure for LocalExecutor instances.

    Args:
        args: arguments used for the command execution
        rc: return code of the executed command
        stdout: output capture
        stderr: error otput capture
    """

    args: list
    rc: int
    stdout: AnyStr | list[AnyStr]
    stderr: AnyStr


class LocalExecutorProtocol(Protocol):
    """Protocol for the LocalExecutor instances."""

    @abc.abstractmethod
    def execute(self, command: str, cwd: Path | None = None) -> LocalExecutionResult:
        """Run command in a implemented way.

        Args:
            command: command to execute
            cwd: current working directory, where to execute a command
        """
        pass


class LocalExecutor(LocalExecutorProtocol):
    """Executes command in local environment, using subprocess.

    Can be used for commands, which ends without any interactive manner.
    """

    def execute(self, command: str, cwd: Path | None = None) -> LocalExecutionResult:
        """Run subprocess and gather the output.

        Args:
            command: command to execute
            cwd: current working directory, where to execute a command
        """
        run_kwargs = {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "shell": True,
        }
        if cwd:
            run_kwargs.update({"cwd": str(cwd)})

        result = subprocess.run(command, **run_kwargs)
        execution_result = LocalExecutionResult(
            args=result.args,
            rc=result.returncode,
            stdout=str(result.stdout),
            stderr=str(result.stderr),
        )

        return execution_result


class LocalPexpectExecutorProtocol(Protocol):
    """Protocol for the LocalPexpectExecutor instances."""

    @abc.abstractmethod
    def execute(
        self, command: str, expect: list[tuple] | None = None, cwd: Path | None = None
    ) -> LocalExecutionResult:
        """Run command in a implemented way.

        Args:
            command: command to execute
            expect: expectation-action pairs for pexpect to handle
            cwd: current working directory, where to execute a command
        """
        pass


class LocalPexpectExecutor(LocalPexpectExecutorProtocol):
    """Executes command in local environment, using Pexpect.

    Can be used to execute interactive commands, which asks for parameters during runtime.
    """

    def execute(
        self,
        command: str,
        expect: list[tuple[str]] | None = None,
        cwd: Path | None = None,
    ) -> LocalExecutionResult:
        """Run command with Pexpect.
        Order:
            - spawns command
            - iterates through list of expects:
                - looks for expected line
                - if found, sends paired line to the stream
            - expects EOF and closes

        Args:
            command: command to execute
            expect: expectation-action pairs for pexpect to handle
                    Tuple must consist of two elements:
                        [0] -> expected text
                        [1] -> command/parameter to send after expected text
            cwd: current working directory, where to execute a command
        """
        output = list()
        child = pexpect.spawn(command, cwd=cwd)
        output.append(child.before)
        for expect_line in expect:

            child.expect(expect_line[0])
            child.sendline(expect_line[1])
            output.append(child.before)
        child.expect(pexpect.EOF)
        child.close()
        output.append(child.before)

        output = [str(line).strip() for line in output if line]
        local_execution_result = LocalExecutionResult(
            args=child.args, rc=child.exitstatus, stderr="", stdout=" ".join(output)
        )
        return local_execution_result
