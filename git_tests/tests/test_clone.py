import shutil
from pathlib import Path

import pytest
from grappa import should

from ..config import PathsConfig, Inventory, SingleGitServerConfig
from ..tools.executors.local_executor import LocalPexpectExecutor
from ..helpers.git_directory_structure import GitDirectoryStructure
from ..helpers.commands.clone_command import CloneCommand


@pytest.mark.order(2)
@pytest.mark.clone
class TestClone:
    paths_config = PathsConfig()
    inventory_config = Inventory()
    single_git_server_config = SingleGitServerConfig()

    local_test_dir_path = Path(paths_config.base_dir, "TMP_TEST_CLONE")
    cloned_repo_path = Path(
        local_test_dir_path, single_git_server_config.test_repo_name
    )

    @pytest.mark.dependency()
    def test_clone_execution(self):
        server_config = self.inventory_config.get(
            self.single_git_server_config.host_name
        )
        local_executor = LocalPexpectExecutor()
        clone_command = CloneCommand(
            command_data={
                "server_config": server_config,
                "single_git_server_config": self.single_git_server_config,
                "cloned_repo_path": self.cloned_repo_path,
            },
            executor=local_executor,
            variant="basic",
        )
        result = clone_command.run()

        result.rc | should.equal.to(0)
        result.stdout | should.contain("Cloning into") | should.contain(
            str(self.cloned_repo_path)
        )

    @pytest.mark.dependency(depends=["TestClone::test_clone_execution"])
    def test_clone_directory_structure(self):
        self.cloned_repo_path.exists() | should.be.true
        self.cloned_repo_path.is_dir() | should.be.true

        git_hidden_dir = Path(self.cloned_repo_path, ".git")
        git_hidden_dir.exists() | should.be.true
        git_hidden_dir.is_dir() | should.be.true

        expected_dirs = GitDirectoryStructure.get_initial_dirs(base_dir=git_hidden_dir)
        for git_dir_path in expected_dirs:
            git_dir_path.exists() | should.be.true
            git_dir_path.is_dir() | should.be.true

        expected_files = GitDirectoryStructure.get_initial_files(
            base_dir=git_hidden_dir
        )
        for git_file_path in expected_files:
            git_file_path.exists() | should.be.true
            git_file_path.is_file() | should.be.true

    @pytest.fixture(scope="class", autouse=True)
    def handle_directory(self):
        if self.local_test_dir_path.exists():
            shutil.rmtree(self.local_test_dir_path)
        self.local_test_dir_path.mkdir()

        yield

        if self.local_test_dir_path.exists():
            shutil.rmtree(self.local_test_dir_path)
