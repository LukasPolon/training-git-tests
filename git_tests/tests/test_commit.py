import re
import shutil
from pathlib import Path

import pytest
from grappa import should

from git_tests.config import PathsConfig, SingleGitServerConfig, Inventory
from git_tests.helpers.commands.clone_command import CloneCommand

from git_tests.helpers.commands.add_command import AddCommand
from git_tests.helpers.commands.commit_command import CommitCommand
from git_tests.helpers.commands.config_command import ConfigCommand
from git_tests.helpers.commands.status_command import StatusCommand
from git_tests.helpers.commands.log_command import LogCommand
from git_tests.tools.executors.local_executor import LocalExecutor, LocalPexpectExecutor


@pytest.mark.order(5)
@pytest.mark.commit
class TestCommit:
    local_executor = LocalExecutor()
    local_pexpect_executor = LocalPexpectExecutor()
    paths_config = PathsConfig()
    single_git_server_config = SingleGitServerConfig()
    inventory_config = Inventory()
    local_test_dir_path = Path(paths_config.base_dir, "TMP_TEST_COMMIT")
    cloned_repo_path = Path(
        local_test_dir_path, single_git_server_config.test_repo_name
    )
    new_file_path = Path(cloned_repo_path, "new_file01")
    new_commit_message = "Test commit message 01"
    server_config = inventory_config.get(single_git_server_config.host_name)

    @pytest.mark.dependency()
    def test_commit_execution(self):
        commit_result = CommitCommand(
            variant="basic", command_data={
                "commit_message": self.new_commit_message,
                "cloned_repo_path": self.cloned_repo_path
            }, executor=self.local_executor
        ).run()
        commit_result.rc | should.be.equal.to(0)
        commit_result.stdout | should.contain("Test commit message 01")
        commit_result.stdout | should.contain(
            "1 file changed, 0 insertions(+), 0 deletions(-)"
        )

    @pytest.mark.dependency(depends=["TestCommit::test_commit_execution"])
    def test_commit_verification(self):
        status_result = StatusCommand(
            variant="basic", command_data={
                "cloned_repo_path": self.cloned_repo_path
            }, executor=self.local_executor
        ).run()
        status_result.rc | should.be.equal.to(0)
        status_result.stdout | should.contain("nothing to commit, working tree clean")

        log_result = LogCommand(
            variant="basic", command_data={
                "cloned_repo_path": self.cloned_repo_path
            }, executor=self.local_executor
        ).run()
        log_result.rc | should.be.equal.to(0)

        output_match = re.search(
            (
                r"[a-zA-Z0-9]{7} "
                rf"{self.new_commit_message}"
            ), str(log_result.stdout)
        )
        isinstance(output_match, re.Match) | should.be.true

    @pytest.fixture(scope="class", autouse=True)
    def prepare_environment(self):
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

        self._create_file()

        add_command_result = AddCommand(
            variant="basic", command_data={
                "new_file_path": self.new_file_path,
                "cloned_repo_path": self.cloned_repo_path,
            }, executor=self.local_executor
        ).run()
        add_command_result.rc | should.be.equal.to(0)

        config_user_result = ConfigCommand(
            variant="user", command_data={
                "cloned_repo_path": self.cloned_repo_path
            }, executor=self.local_executor
        ).run()
        config_user_result.rc | should.be.equal.to(0)

        config_user_result = ConfigCommand(
            variant="email", command_data={
                "cloned_repo_path": self.cloned_repo_path
            }, executor=self.local_executor
        ).run()
        config_user_result.rc | should.be.equal.to(0)

        yield

        if self.local_test_dir_path.exists():
            shutil.rmtree(self.local_test_dir_path)

    def _create_file(self):
        new_file_path = Path(self.cloned_repo_path, "new_file01")
        new_file_path.touch()
        new_file_path.is_file() | should.be.true
