from typing import Literal, Any, Callable, Type

from git_tests.helpers.commands.command_protocol import CommandProtocol
from git_tests.tools.executors.local_executor import (
    LocalExecutorProtocol,
    LocalExecutor,
)


class ConfigCommand(CommandProtocol):
    def __init__(
        self,
        variant: Literal["user", "email"],
        command_data: dict[str, Any],
        executor: LocalExecutor,
    ) -> None:
        self.__variant = variant
        self.__command_data = command_data
        self.__executor = executor

    def run(self):
        result = self.__executor.execute(
            **self.__get_mapped_variants()[self.__variant]()
        )
        return result

    def __get_mapped_variants(self) -> dict[str, Callable]:
        variants = {"user": self.__get_user_variant, "email": self.__get_email_variant}
        return variants

    def __get_user_variant(self):
        variant = {
            "command": 'git config --local user.name "gituser"',
            "cwd": self.__command_data.get("cloned_repo_path"),
        }
        return variant

    def __get_email_variant(self):
        variant = {
            "command": 'git config --local user.email "email@example.com"',
            "cwd": self.__command_data.get("cloned_repo_path"),
        }
        return variant
