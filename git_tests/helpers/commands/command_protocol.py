import abc
from typing import Protocol, Type, Any, Literal

from git_tests.tools.executors.local_executor import (
    LocalExecutorProtocol,
    LocalExecutionResult,
)


class CommandProtocol(Protocol):

    executor: Type[LocalExecutorProtocol]
    command_data: dict[str, Any]
    variant: str

    @abc.abstractmethod
    def run(self) -> LocalExecutionResult:
        pass
