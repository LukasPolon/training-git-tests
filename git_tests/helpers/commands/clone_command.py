from typing import Any, Literal, Callable

from git_tests.helpers.commands.command_protocol import CommandProtocol
from git_tests.tools.executors.local_executor import (
    LocalExecutionResult,
    LocalPexpectExecutor,
)


class CloneCommand(CommandProtocol):
    """Wrapper for "git clone" command."""

    def __init__(
        self,
        variant: Literal["basic"],
        command_data: dict[
            Literal["server_config", "single_git_server_config", "cloned_repo_path"],
            Any,
        ],
        executor: LocalPexpectExecutor,
    ) -> None:
        """Constructor method for CloneCommand.

        executor: Executor instance to use for running the command
        command_data: data needed for command execution
        variant: command variant to execute
        """
        self.__variant = variant
        self.__command_data = command_data
        self.__executor = executor

    def run(self) -> LocalExecutionResult:
        """Runs command with selected arguments."""
        result = self.__executor.execute(
            **self.__get_mapped_variants()[self.__variant]()
        )
        return result

    def __get_mapped_variants(self) -> dict[str, Callable]:
        """Returns variant names and their callable methods mapped."""
        variants = {"basic": self.__get_basic_variant}
        return variants

    def __get_basic_variant(self) -> dict[str, Any]:
        """Variant: basic for "git clone"."""
        variant = {
            "command": (
                f"git clone ssh://{self.__command_data.get('server_config').ansible_user}@"
                f"{self.__command_data.get('server_config').ansible_host}"
                f"{str(self.__command_data.get('single_git_server_config').repos_path)}/"
                f"{self.__command_data.get('single_git_server_config').test_repo_name} "
                f"{str(self.__command_data.get('cloned_repo_path'))}"
            ),
            "expect": [
                (
                    f"{self.__command_data.get('server_config').ansible_user}@{self.__command_data.get('server_config').ansible_host}'s password:",
                    f"{self.__command_data.get('server_config').ansible_password}\n",
                )
            ],
        }
        return variant
