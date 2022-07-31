from typing import Literal, Any, Callable

from git_tests.helpers.commands.command_protocol import CommandProtocol
from git_tests.tools.executors.local_executor import LocalExecutor, LocalExecutionResult


class LogCommand(CommandProtocol):
    def __init__(
        self,
        variant: Literal["basic"],
        command_data: dict[str, Any],
        executor: LocalExecutor,
    ) -> None:
        self.__variant = variant
        self.__command_data = command_data
        self.__executor = executor

    def run(self) -> LocalExecutionResult:
        result = self.__executor.execute(
            **self.__get_mapped_variants()[self.__variant]()
        )
        return result

    def __get_mapped_variants(self) -> dict[str, Callable]:
        variants = {"basic": self.__get_basic_variant}
        return variants

    def __get_basic_variant(self) -> dict[str, Any]:
        variant = {
            "command": f"git log --oneline",
            "cwd": self.__command_data.get("cloned_repo_path"),
        }
        return variant
