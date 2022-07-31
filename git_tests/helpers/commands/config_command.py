from typing import Literal, Any, Callable

from git_tests.helpers.commands.command_protocol import CommandProtocol
from git_tests.tools.executors.local_executor import LocalExecutor


class ConfigCommand(CommandProtocol):
    """Wrapper for "git config" command."""

    def __init__(
        self,
        variant: Literal["user", "email"],
        command_data: dict[Literal["cloned_repo_path"], Any],
        executor: LocalExecutor,
    ) -> None:
        """Constructor method for ConfigCommand.

        executor: Executor instance to use for running the command
        command_data: data needed for command execution
        variant: command variant to execute
        """
        self.__variant = variant
        self.__command_data = command_data
        self.__executor = executor

    def run(self):
        """Runs command with selected arguments."""
        result = self.__executor.execute(
            **self.__get_mapped_variants()[self.__variant]()
        )
        return result

    def __get_mapped_variants(self) -> dict[str, Callable]:
        """Returns variant names and their callable methods mapped."""
        variants = {"user": self.__get_user_variant, "email": self.__get_email_variant}
        return variants

    def __get_user_variant(self):
        """Variant: user for "git config"."""
        variant = {
            "command": 'git config --local user.name "gituser"',
            "cwd": self.__command_data.get("cloned_repo_path"),
        }
        return variant

    def __get_email_variant(self):
        """Variant: email for "git config"."""
        variant = {
            "command": 'git config --local user.email "email@example.com"',
            "cwd": self.__command_data.get("cloned_repo_path"),
        }
        return variant
