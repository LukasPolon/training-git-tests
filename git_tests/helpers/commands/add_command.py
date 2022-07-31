from typing import Any, Callable, Literal

from git_tests.helpers.commands.command_protocol import CommandProtocol
from git_tests.tools.executors.local_executor import LocalExecutor, LocalExecutionResult


class AddCommand(CommandProtocol):
    """Wrapper for "git add" command."""

    def __init__(
        self,
        variant: Literal["basic"],
        command_data: dict[Literal["new_file_path", "cloned_repo_path"], Any],
        executor: LocalExecutor,
    ) -> None:
        """Constructor method for AddCommand.

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
        """Variant: basic for "git add"."""
        variant = {
            "command": f"git add {self.__command_data.get('new_file_path').name}",
            "cwd": self.__command_data.get("cloned_repo_path"),
        }
        return variant
