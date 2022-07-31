import abc
import subprocess
from dataclasses import dataclass
from subprocess import Popen
from pathlib import Path
from typing import Protocol, AnyStr, Any

import pexpect


@dataclass
class LocalExecutionResult:
    args: list
    rc: int
    stdout: AnyStr | list[AnyStr]
    stderr: AnyStr


class LocalExecutorProtocol(Protocol):
    @abc.abstractmethod
    def execute(self, command: str, **kwargs: Any) -> LocalExecutionResult:
        pass


class LocalExecutor(LocalExecutorProtocol):
    def execute(self, command: str, cwd: Path | None = None) -> LocalExecutionResult:

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


class LocalPexpectExecutor(LocalExecutorProtocol):
    def execute(
        self, command: str, expect: list[tuple] | None = None, cwd: Path | None = None
    ) -> LocalExecutionResult:
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
