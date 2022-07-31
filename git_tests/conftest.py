import pytest
from .config import PathsConfig
from .tools.executors.ansible_executor import AnsibleExecutor


@pytest.fixture(scope="session", autouse=True)
def run_initial_env_configuration() -> None:
    """Runs once, before any tests.

    Runs Ansible Playbooks:
        - test environment configuration (test container)
        - GIT installation (test container, git server container)
        - server configuration (git server container)

    Must be executed in that order.
    """
    paths_config = PathsConfig()
    ansible_executor = AnsibleExecutor()

    configure_test_env(paths_config=paths_config, ansible_executor=ansible_executor)
    install_git(paths_config=paths_config, ansible_executor=ansible_executor)
    configure_server_env(paths_config=paths_config, ansible_executor=ansible_executor)


def configure_test_env(
    paths_config: PathsConfig, ansible_executor: AnsibleExecutor
) -> None:
    result = ansible_executor.execute(
        inventory=paths_config.ansible_inventory_file,
        playbook=paths_config.playbook_tests_env_config,
    )
    assert result.status == "successful"


def configure_server_env(
    paths_config: PathsConfig, ansible_executor: AnsibleExecutor
) -> None:
    result = ansible_executor.execute(
        inventory=paths_config.ansible_inventory_file,
        playbook=paths_config.playbook_server_config,
    )
    assert result.status == "successful"


def install_git(paths_config: PathsConfig, ansible_executor: AnsibleExecutor) -> None:
    result = ansible_executor.execute(
        inventory=paths_config.ansible_inventory_file,
        playbook=paths_config.playbook_install_git,
    )
    assert result.status == "successful"
