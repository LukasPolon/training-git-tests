import os
import yaml

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class PathsConfig:
    """Paths configuration.
    Should contain Paths to static files and directories in the project.
    """

    tests_dir: Path = Path(os.path.dirname(__file__)).resolve()
    base_dir: Path = Path(tests_dir, "..").resolve()
    playbooks_dir: Path = Path(base_dir, "playbooks")

    playbook_install_git: Path = Path(playbooks_dir, "install_git.yaml")
    playbook_server_config: Path = Path(playbooks_dir, "server_config.yaml")
    playbook_tests_env_config: Path = Path(playbooks_dir, "tests_env_config.yaml")

    ansible_inventory_file: Path = Path(base_dir, "inventory.yaml")


@dataclass
class InventoryHost:
    """Representation of one host from Inventory.
    In order to be created, host must have defined all variables starting with ansible_.
    """

    name: str
    ansible_host: str
    ansible_user: str
    ansible_password: str

    _full_data: field(init=False, repr=False, kw_only=True) = False

    def __post_init__(self) -> None:
        """Executes after initialization.
        Checks if all ansible_ data are present.
        """
        if all([self.ansible_host, self.ansible_user, self.ansible_password]):
            self._full_data = True

    def all_data_collected(self) -> bool:
        """Getter for _full_data field."""
        return self._full_data


@dataclass
class Inventory:
    """Ansible Inventory file representation. Gathers Hosts information."""

    hosts: list[InventoryHost] = field(default_factory=list)

    def __post_init__(self):
        """Parses inventory.yaml file and fills hosts with InventoryHost."""
        if not self.hosts:
            with open(PathsConfig().ansible_inventory_file, "r") as inventory:
                inventory_data = yaml.load(inventory, Loader=yaml.SafeLoader)
                for host_name, host_data in (
                    inventory_data.get("all").get("hosts").items()
                ):
                    inventory_host = InventoryHost(
                        name=host_name,
                        ansible_host=host_data.get("ansible_host"),
                        ansible_user=host_data.get("ansible_user"),
                        ansible_password=host_data.get("ansible_password"),
                    )
                    if inventory_host.all_data_collected():
                        self.hosts.append(inventory_host)

    def get(self, name: str) -> InventoryHost:
        """Returns host by its name."""
        for host in self.hosts:
            if host.name == name:
                host_to_return = host
                break
        else:
            raise ValueError(f"Not found Host with name: {name}.")
        return host_to_return


@dataclass
class SingleGitServerConfig:
    """Configuration for single GIT server.

    Args:
        host_name: typically, container name
        repos_path: main repository directory on the host, configured by the playbook
        test_repo_name: test repository name on the host, configured by the playbook
    """

    host_name: str = "git-server-custom"
    repos_path: Path = Path("/git-repos")
    test_repo_name: str = "testrepo.git"
