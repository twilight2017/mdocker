class MDockerError(Exception):
    pass


class CFileNotFoundError(MDockerError):
    """关键文件不存在错误"""
