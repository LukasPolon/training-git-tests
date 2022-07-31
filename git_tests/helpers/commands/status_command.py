from typing import Literal, Any, Callable

from git_tests.helpers.commands.command_protocol import CommandProtocol
from git_tests.tools.executors.local_executor import LocalExecutor, LocalExecutionResult


class StatusCommand(CommandProtocol):
    """Wrapper for "git status" command."""

    def __init__(
        self,
        variant: Literal["basic"],
        command_data: dict[Literal["cloned_repo_path"], Any],
        executor: LocalExecutor,
    ) -> None:
        """Constructor method for StatusCommand.

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
        """Variant: basic for "git status"."""
        variant = {
            "command": "git status",
            "cwd": self.__command_data.get("cloned_repo_path"),
        }
        return variant
