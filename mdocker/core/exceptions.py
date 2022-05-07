class MDockerError(Exception):
    def __init__(self, msg=None, detail=None, payload=None):
        self.detail = detail
        if detail:
            msg += f' ({detail})'
        super().__init__(msg)  # super()调用父类方法
        self.payload = payload


class CFileNotFoundError(MDockerError):
    """
    关键文件不存在-Error
    如果文件不存在，则抛出此异常
    """
    pass


class HashMismatch(MDockerError):
    pass


class InvalidTOML(MDockerError):
    pass


class ProjectDoesNotExist(MDockerError):
    pass


class DockerError(MDockerError):
    pass