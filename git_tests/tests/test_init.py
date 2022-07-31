import shutil
from pathlib import Path
from grappa import should

import pytest

from ..tools.executors.local_executor import LocalExecutor
from ..config import PathsConfig
from ..helpers.git_directory_structure import GitDirectoryStructure
from ..helpers.commands.init_command import InitCommand


@pytest.mark.order(1)
@pytest.mark.init
class TestInit:
    """Verification of git init command."""

    paths_config = PathsConfig()
    local_test_dir_path = Path(paths_config.base_dir, "TMP_TEST_INIT")
    git_repo_path_working = Path(local_test_dir_path, "testrepo_working")
    git_repo_path_bare = Path(local_test_dir_path, "testrepo_bare")

    @pytest.mark.dependency()
    def test_init_working_creation(self):
        """
        Given:
            - local environment with created directory for repository
        When:
            - executing "git init" command, creating the working repository
        Then:
            - command ends with success and right output
        """
        local_executor = LocalExecutor()
        result = InitCommand(
            variant="basic",
            command_data={"git_repo_path": self.git_repo_path_working},
            executor=local_executor,
        ).run()
        result.rc | should.be.equal.to(0, msg="Command exited with Exit code != 0")
        result.stdout | should.contain(
            f"Initialized empty Git repository in {self.git_repo_path_working}/.git/"
        )

    @pytest.mark.dependency(depends=["TestInit::test_init_working_creation"])
    def test_init_working_directory_content(self):
        """
        Given:
            - successfully executed "git init" command
        When: -
        Then:
            - new working repository exists
            - .git directory contains right structure if files and directories
        """
        self.git_repo_path_working.exists() | should.be.true
        self.git_repo_path_working.is_dir() | should.be.true

        git_hidden_dir = Path(self.git_repo_path_working, ".git")
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

    @pytest.mark.dependency()
    def test_init_bare_creation(self):
        """
        Given:
            - local environment with created directory for repository
        When:
            , creating bare repository
        Then:
            - command ends with success and right output
        """
        local_executor = LocalExecutor()
        result = InitCommand(
            variant="bare",
            command_data={"git_repo_path": self.git_repo_path_bare},
            executor=local_executor,
        ).run()
        result.rc | should.be.equal.to(0, msg="Command exited with Exit code != 0")
        result.stdout | should.contain(
            f"Initialized empty Git repository in {self.git_repo_path_bare}"
        )

    @pytest.mark.dependency(depends=["TestInit::test_init_bare_creation"])
    def test_init_bare_directory_content(self):
        """
        Given:
            - successfully executed "git init --bare" command
        When: -
        Then:
            - new bare repository exists
            - directory contains right structure if files and directories
        """
        self.git_repo_path_bare.exists() | should.be.true
        self.git_repo_path_bare.is_dir() | should.be.true

        expected_dirs = GitDirectoryStructure.get_initial_dirs(
            base_dir=self.git_repo_path_bare
        )
        for git_dir_path in expected_dirs:
            git_dir_path.exists() | should.be.true
            git_dir_path.is_dir() | should.be.true

        expected_files = GitDirectoryStructure.get_initial_files(
            base_dir=self.git_repo_path_bare
        )
        for git_file_path in expected_files:
            git_file_path.exists() | should.be.true
            git_file_path.is_file() | should.be.true

    @pytest.fixture(scope="class", autouse=True)
    def handle_directory(self):
        """Setup/Teardown fixture.
        Creates and deletes directory for the test.
        """
        if self.local_test_dir_path.exists():
            shutil.rmtree(self.local_test_dir_path)
        self.local_test_dir_path.mkdir()

        yield

        if self.local_test_dir_path.exists():
            shutil.rmtree(self.local_test_dir_path)
