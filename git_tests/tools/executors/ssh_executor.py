import abc
from dataclasses import dataclass
from typing import Protocol, Literal

import paramiko


@dataclass
class SshHostData:
    host: str
    user: str
    password: str


@dataclass
class SshExecutionResult:
    stdin: paramiko.channel.ChannelFile
    stdout: paramiko.channel.ChannelFile
    stderr: paramiko.channel.ChannelFile

    def read(self, stream: Literal["stdin", "stdout", "stderr"]) -> list[str]:
        return getattr(self, stream).readlines()



class SshExecutorProtocol(Protocol):

    host_data: SshHostData

    @abc.abstractmethod
    def execute(self, command: str) -> SshExecutionResult:
        pass


class SshExecutor(SshExecutorProtocol):
    def __init__(self, host_data: SshHostData) -> None:
        self.__host_data = host_data
        self.__client = None

    def __enter__(self):
        self.__client = paramiko.SSHClient()
        self.__client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        self.__client.connect(
            hostname=self.__host_data.host,
            username=self.__host_data.user,
            password=self.__host_data.password,
        )
        return self

    def __exit__(self, *exc):
        self.__client.close()

    def execute(self, command: str) -> SshExecutionResult:
        result = self.__client.exec_command(command, timeout=10)
        execution_result = SshExecutionResult(
            stdin=result[0],
            stdout=result[1],
            stderr=result[2]
        )
        return execution_result

