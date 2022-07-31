import re
import shutil
from pathlib import Path

import pytest
from grappa import should

from git_tests.config import PathsConfig, SingleGitServerConfig, Inventory
from git_tests.helpers.commands.add_command import AddCommand
from git_tests.helpers.commands.checkout_command import CheckoutCommand
from git_tests.helpers.commands.clone_command import CloneCommand
from git_tests.helpers.commands.commit_command import CommitCommand
from git_tests.helpers.commands.config_command import ConfigCommand
from git_tests.helpers.commands.push_command import PushCommand
from git_tests.tools.executors.local_executor import LocalExecutor, LocalPexpectExecutor
from git_tests.tools.executors.ssh_executor import SshExecutor, SshHostData


@pytest.mark.order(6)
@pytest.mark.push
class TestPush:
    """Verification of git push command."""

    local_executor = LocalExecutor()
    local_pexpect_executor = LocalPexpectExecutor()
    paths_config = PathsConfig()
    single_git_server_config = SingleGitServerConfig()
    inventory_config = Inventory()
    local_test_dir_path = Path(paths_config.base_dir, "TMP_TEST_PUSH")
    cloned_repo_path = Path(
        local_test_dir_path, single_git_server_config.test_repo_name
    )
    server_config = inventory_config.get(single_git_server_config.host_name)
    new_branch_name = "new_branch_01"
    new_file_path = Path(cloned_repo_path, "new_file01")
    new_commit_message = "new_commit message 01"

    def test_push_to_origin(self):
        """
        Given:
            - local environment with created directory for repository
            - cloned remote repository
            - created and moved to a new branch
            - created a new file and added to staging
            - user and email configured in local git config
            - created a new commit to push
            - remote server confirms no commits
        When:
            - executing "git push origin <branch>"
        Then:
            - command ends with success and right output
            - remote server confirms received commit through git log command
        """
        host_data = SshHostData(
            user=self.server_config.ansible_user,
            password=self.server_config.ansible_password,
            host=self.server_config.ansible_host,
        )

        origin_repo_path = Path(
            self.single_git_server_config.repos_path,
            self.single_git_server_config.test_repo_name,
        )
        # TODO: Can be refactored to be another CommandProtocol implementation
        with SshExecutor(host_data=host_data) as ssh_executor:
            result = ssh_executor.execute(f"cd {origin_repo_path}; git log --oneline")
            stderr_content = result.read(channel="stderr")
        stderr_content | should.have.length.of(1)
        stderr_content[0] | should.contain(
            "fatal: your current branch 'master' does not have any commits yet"
        )

        push_result = PushCommand(
            variant="basic",
            command_data={
                "new_branch_name": self.new_branch_name,
                "cloned_repo_path": self.cloned_repo_path,
                "server_config": self.server_config,
            },
            executor=self.local_pexpect_executor,
        ).run()
        push_result.rc | should.be.equal.to(0)
        push_result.stdout | should.contain("Writing objects: 100%")
        push_result.stdout | should.contain(
            f"{self.new_branch_name} -> {self.new_branch_name}"
        )

        with SshExecutor(host_data=host_data) as ssh_executor:
            result = ssh_executor.execute(
                f"cd {origin_repo_path}; git log --oneline --branches {self.new_branch_name}"
            )
            stdout_content = result.read(channel="stdout")
            stdout_content | should.have.length.of(1)

            match_content = re.match(
                (r"[a-zA-Z0-9]{7} " rf"{self.new_commit_message}"), stdout_content[0]
            )
            isinstance(match_content, re.Match) | should.be.true

    @pytest.fixture(scope="class", autouse=True)
    def prepare_environment(self):
        # TODO: it is way too long, must be divided or logic must be changed
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

        checkout_command = CheckoutCommand(
            variant="branch",
            command_data={
                "branch_name": self.new_branch_name,
                "cloned_repo_path": self.cloned_repo_path,
            },
            executor=self.local_executor,
        ).run()
        checkout_command.rc | should.be.equal.to(0)

        self.new_file_path.touch()
        self.new_file_path.is_file() | should.be.true

        add_command = AddCommand(
            variant="basic",
            command_data={
                "new_file_path": self.new_file_path,
                "cloned_repo_path": self.cloned_repo_path,
            },
            executor=self.local_executor,
        ).run()

        add_command.rc | should.be.equal.to(0)

        config_user_result = ConfigCommand(
            variant="user",
            command_data={"cloned_repo_path": self.cloned_repo_path},
            executor=self.local_executor,
        ).run()
        config_user_result.rc | should.be.equal.to(0)

        config_user_result = ConfigCommand(
            variant="email",
            command_data={"cloned_repo_path": self.cloned_repo_path},
            executor=self.local_executor,
        ).run()
        config_user_result.rc | should.be.equal.to(0)

        commit_command = CommitCommand(
            variant="basic",
            command_data={
                "commit_message": self.new_commit_message,
                "cloned_repo_path": self.cloned_repo_path,
            },
            executor=self.local_executor,
        ).run()
        commit_command.rc | should.be.equal.to(0)

        yield

        if self.local_test_dir_path.exists():
            shutil.rmtree(self.local_test_dir_path)
