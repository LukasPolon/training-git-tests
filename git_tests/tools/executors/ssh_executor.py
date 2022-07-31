import abc
from dataclasses import dataclass
from typing import Protocol, Literal, TypeVar

import paramiko


TypeSshExecutor = TypeVar("TypeSshExecutor", bound="SshExecutor")


@dataclass
class SshHostData:
    """Host connection data for SshExecutor.

    Args:
        host: hostname to connect
        user: username to connect
        password: password to use
    """

    host: str
    user: str
    password: str


@dataclass
class SshExecutionResult:
    """Result structure for SshExecutor instances.

    Args:
        stdin: input channel
        stdout: general output channel
        stderr: error output channel

    Channels works like files, so they can be read only if they are open.
    """

    stdin: paramiko.channel.ChannelFile
    stdout: paramiko.channel.ChannelFile
    stderr: paramiko.channel.ChannelFile

    def read(self, channel: Literal["stdin", "stdout", "stderr"]) -> list[str]:
        """Read content of the selected channel.

        Args:
            channel: which channel to read

        Returns:
            content of a selected channel
        """
        return getattr(self, channel).readlines()


class SshExecutorProtocol(Protocol):
    """Protocol for the SshExecutor instances.

    Args:
        host_data: host connection information
    """

    host_data: SshHostData

    @abc.abstractmethod
    def execute(self, command: str) -> SshExecutionResult:
        """Run command in a implemented way.

        Args:
            command: command to execute
        """
        pass


class SshExecutor(SshExecutorProtocol):
    """Executes command in remote environment, using Ssh.

    Can be used as Context Manager:
        with SshExecutor(host_data) as ssh_executor:
            ssh_executor.execute()
    """

    def __init__(self, host_data: SshHostData) -> None:
        """Constructor method for SshExecutor.

        Args:
            host_data: host connection information
        """
        self.__host_data = host_data
        self.__client = None

    def __enter__(self) -> TypeSshExecutor:
        """Enter method for Context Manager.
        Creates SSH client and starts the connection.

        Returns:
            SshExecutor instance
        """
        self.__client = paramiko.SSHClient()
        self.__client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        self.__client.connect(
            hostname=self.__host_data.host,
            username=self.__host_data.user,
            password=self.__host_data.password,
        )
        return self

    def __exit__(self, *exc):
        """Invoked after exiting Context Manager block.
        Closes the Ssh connection.
        """
        self.__client.close()

    def execute(self, command: str) -> SshExecutionResult:
        """Executes command through Ssh.

        Args:
            command: to execute

        Returns:
            execution_result: gathered result data
        """
        result = self.__client.exec_command(command, timeout=10)
        execution_result = SshExecutionResult(
            stdin=result[0], stdout=result[1], stderr=result[2]
        )
        return execution_result
