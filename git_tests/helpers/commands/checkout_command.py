from typing import Literal, Any, Callable

from git_tests.helpers.commands.command_protocol import CommandProtocol
from git_tests.tools.executors.local_executor import LocalExecutor, LocalExecutionResult


class CheckoutCommand(CommandProtocol):
    def __init__(
        self,
        variant: Literal["branch"],
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
        variants = {"branch": self.__get_basic_variant}
        return variants

    def __get_basic_variant(self) -> dict[str, Any]:
        variant = {
            "command": f"git checkout -b {self.__command_data.get('branch_name')}",
            "cwd": self.__command_data.get("cloned_repo_path"),
        }
        return variant
