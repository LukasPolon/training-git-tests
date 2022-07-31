# TODO: some code is repeated between implementations, classic ABC can be considered
import abc
from typing import Protocol, Type, Any

from git_tests.tools.executors.local_executor import (
    LocalExecutorProtocol,
    LocalExecutionResult,
)


class CommandProtocol(Protocol):
    """Protocol for the Command implementations.

    Args:
        executor: Executor instance to use for running the command
        command_data: data needed for command execution
        variant: command variant to execute
    """

    executor: Type[LocalExecutorProtocol]
    command_data: dict[str, Any]
    variant: str

    @abc.abstractmethod
    def run(self) -> LocalExecutionResult:
        """Runs command according to arguments."""
        pass
