import shutil
from pathlib import Path

import pytest
from grappa import should

from git_tests.config import PathsConfig, Inventory, SingleGitServerConfig
from git_tests.helpers.commands.clone_command import CloneCommand
from git_tests.helpers.commands.checkout_command import CheckoutCommand
from git_tests.helpers.commands.status_command import StatusCommand
from git_tests.tools.executors.local_executor import LocalExecutor, LocalPexpectExecutor


@pytest.mark.order(4)
@pytest.mark.checkout
class TestCheckout:
    """Verification of git checkout command."""

    local_executor = LocalExecutor()
    local_pexpect_executor = LocalPexpectExecutor()
    paths_config = PathsConfig()
    single_git_server_config = SingleGitServerConfig()
    inventory_config = Inventory()
    local_test_dir_path = Path(paths_config.base_dir, "TMP_TEST_CHECKOUT")
    cloned_repo_path = Path(
        local_test_dir_path, single_git_server_config.test_repo_name
    )
    new_branch_name = "new_branch_01"
    server_config = inventory_config.get(single_git_server_config.host_name)

    def test_checkout_to_new_branch(self):
        """
        Given:
            - local environment with created directory for repository
            - cloned remote repository
            - git status confirms that current branch is master
        When:
            - executing "git checkout -b <branch>" command
        Then:
            - command ends with success and right output
            - git status confirms branch change
        """
        status_result = StatusCommand(
            variant="basic",
            command_data={"cloned_repo_path": self.cloned_repo_path},
            executor=self.local_executor,
        ).run()
        status_result.rc | should.be.equal.to(0)
        status_result.stdout | should.contain("On branch master")

        checkout_result = CheckoutCommand(
            variant="branch",
            command_data={
                "branch_name": self.new_branch_name,
                "cloned_repo_path": self.cloned_repo_path,
            },
            executor=self.local_executor,
        ).run()
        checkout_result.rc | should.be.equal.to(0)
        checkout_result.stderr | should.contain(
            "Switched to a new branch"
        ) | should.contain(self.new_branch_name)

        status_result = StatusCommand(
            variant="basic",
            command_data={"cloned_repo_path": self.cloned_repo_path},
            executor=self.local_executor,
        ).run()
        status_result.rc | should.be.equal.to(0)
        status_result.stdout | should.contain(f"On branch {self.new_branch_name}")

    @pytest.fixture(scope="class", autouse=True)
    def prepare_environment(self):
        """Setup/Teardown fixture.
        Creates and deletes directory for the test.
        Runs git clone command.
        """
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
