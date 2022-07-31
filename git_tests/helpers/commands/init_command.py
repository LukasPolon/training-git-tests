from typing import Any, Literal, Callable

from git_tests.helpers.commands.command_protocol import CommandProtocol
from git_tests.tools.executors.local_executor import LocalExecutionResult, LocalExecutor


class InitCommand(CommandProtocol):
    def __init__(
        self,
        variant: Literal["basic", "bare"],
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
        variants = {"basic": self.__get_basic_variant, "bare": self.__get_bare_variant}
        return variants

    def __get_basic_variant(self) -> dict[str, Any]:
        variant = {
            "command": f"git init {str(self.__command_data.get('git_repo_path'))}"
        }
        return variant

    def __get_bare_variant(self) -> dict[str, Any]:
        variant = {
            "command": f"git init {str(self.__command_data.get('git_repo_path'))} --bare"
        }
        return variant
