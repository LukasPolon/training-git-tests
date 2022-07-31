from typing import Literal, Any, Callable

from git_tests.helpers.commands.command_protocol import CommandProtocol
from git_tests.tools.executors.local_executor import LocalExecutor, LocalExecutionResult


class CheckoutCommand(CommandProtocol):
    """Wrapper for "git checkout" command."""

    def __init__(
        self,
        variant: Literal["branch"],
        command_data: dict[Literal["branch_name", "cloned_repo_path"], Any],
        executor: LocalExecutor,
    ) -> None:
        """Constructor method for CheckoutCommand.

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
        variants = {"branch": self.__get_branch_variant}
        return variants

    def __get_branch_variant(self) -> dict[str, Any]:
        """Variant: branch for "git checkout"."""
        variant = {
            "command": f"git checkout -b {self.__command_data.get('branch_name')}",
            "cwd": self.__command_data.get("cloned_repo_path"),
        }
        return variant
