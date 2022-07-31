import re
import shutil
from pathlib import Path
from re import Match

import pytest
from grappa import should


from git_tests.config import PathsConfig, SingleGitServerConfig, Inventory
from git_tests.tools.executors.local_executor import (
    LocalExecutor,
    LocalExecutionResult,
    LocalPexpectExecutor,
)
from git_tests.helpers.commands.clone_command import CloneCommand
from git_tests.helpers.commands.add_command import AddCommand
from git_tests.helpers.commands.status_command import StatusCommand


@pytest.mark.order(3)
@pytest.mark.add
class TestAdd:
    local_executor = LocalExecutor()
    local_pexpect_executor = LocalPexpectExecutor()
    paths_config = PathsConfig()
    inventory_config = Inventory()
    single_git_server_config = SingleGitServerConfig()
    server_config = inventory_config.get(single_git_server_config.host_name)

    local_test_dir_path = Path(paths_config.base_dir, "TMP_TEST_ADD")

    cloned_repo_path = Path(
        local_test_dir_path, single_git_server_config.test_repo_name
    )

    def test_add_one_file(self):
        new_file_path = Path(self.cloned_repo_path, "new_file01")
        new_file_path.touch()
        new_file_path.is_file() | should.be.true

        # TODO: may be unstable, need to find a better way, starting with cleaning the output
        result_status = self._run_status()
        status_info = re.search(
            (
                r".*(Untracked files:\\n\s+\("
                r"use \"git add <file>...\" to include in "
                rf"what will be committed\)\\n\\t{new_file_path.name})"
            ),
            result_status.stdout,
        )
        isinstance(status_info, Match) | should.be.true

        result_add = AddCommand(
            variant="basic",
            command_data={
                "new_file_path": new_file_path,
                "cloned_repo_path": self.cloned_repo_path,
            },
            executor=self.local_executor,
        ).run()
        result_add.rc | should.be.equal.to(0)

        result_status = self._run_status()
        status_info = re.search(
            (
                r".*(Changes to be committed:\\n\s+"
                r"\(use \"git rm --cached <file>...\" to unstage\)\\n\\t"
                rf"new file:\s+{new_file_path.name})"
            ),
            result_status.stdout,
        )
        isinstance(status_info, Match) | should.be.true

    def _run_status(self) -> LocalExecutionResult:
        result_status = StatusCommand(
            variant="basic",
            command_data={"cloned_repo_path": self.cloned_repo_path},
            executor=self.local_executor
        ).run()
        result_status.rc | should.be.equal.to(0)
        return result_status

    @pytest.fixture(scope="class", autouse=True)
    def handle_directory(self):

        if self.local_test_dir_path.exists():
            shutil.rmtree(self.local_test_dir_path)
        self.local_test_dir_path.mkdir()

        clone_command = CloneCommand(
            variant="basic",
            command_data={
                "server_config": self.server_config,
                "single_git_server_config": self.single_git_server_config,
                "cloned_repo_path": self.cloned_repo_path,
            },
            executor=self.local_pexpect_executor,
        ).run()
        clone_command.rc | should.be.equal.to(0)

        yield

        if self.local_test_dir_path.exists():
            shutil.rmtree(self.local_test_dir_path)
