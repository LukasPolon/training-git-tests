# TODO: can be covered by Adapter pattern
import abc
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Literal
from ansible_runner.interface import run


@dataclass
class AnsibleResultStats:
    """Result structure for Ansible Playbook stats."""

    skipped: dict[str, int]
    ok: dict[str, int]
    dark: dict[str, int]
    failures: dict[str, int]
    ignored: dict[str, int]
    rescued: dict[str, int]
    processed: dict[str, int]
    changed: dict[str, int]


@dataclass
class AnsibleExecutorResult:
    """Result structure for AnsibleExecutor instances.

    Args:
        status: Playbook execution status
        stats: stats collected by Playbook
    """

    status: Literal[
        "starting", "running", "canceled", "timeout", "failed", "successful"
    ]
    stats: AnsibleResultStats


class AnsibleExecutorProtocol(Protocol):
    """Protocol for the AnsibleExecutor instances."""

    @abc.abstractmethod
    def execute(self, playbook: Path, inventory: Path) -> AnsibleExecutorResult:
        """Run Ansible Playbook.

        Args:
            playbook: path to the playbook to play
            inventory: path to the inventory file
        """
        pass


class AnsibleExecutor(AnsibleExecutorProtocol):
    """Runs Ansible Playbooks."""

    def execute(self, playbook: Path, inventory: Path) -> AnsibleExecutorResult:
        """Run Ansible Playbook.

        Args:
            playbook: path to the playbook to play
            inventory: path to the inventory file
        """
        # TODO: error handling needed
        # TODO: full Ansible log storage needed
        run_result = run(playbook=str(playbook), inventory=str(inventory), quiet=True)
        executor_result = AnsibleExecutorResult(
            status=run_result.status, stats=AnsibleResultStats(**run_result.stats)
        )
        return executor_result
