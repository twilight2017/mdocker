class MDockerError(Exception):
    def __init__(self, msg=None, detail=None, payload=None):
        self.msg = msg
        self.detail = detail
        self.payload = payload
        super().__init__(msg)

    def __str__(self):
        msg = self.msg
        if self.detail:
            msg += f'({self.detail})'
        return msg


class CFileNotFoundError(MDockerError):
    """
    关键文件不存在-error
    如果文件不存在，则抛出此异常
    """
    pass


class HashMismatch(MDockerError):
    pass


class InvaildToml(MDockerError):
    pass


class InvaildConfiguration(MDockerError):
    pass


class InvaildRepo(MDockerError):
    pass


class DockerError(MDockerError):
    pass
