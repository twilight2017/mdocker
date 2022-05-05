"""检查必要文件是否存在"""
import pathlib
from dataclasses import dataclass
from .exceptions import CFileNotFoundError
from typing import List


@dataclass
class CritialFile:
    filename: str
    filepath: pathlib.Path
    remark: str
    prefix: pathlib.Path

    def has_file(self):
        full_path = self.prefix / self.filepath # pathlib模块可以直接用/拼接文件路径
        return full_path.exists()


@dataclass
class Checker:
    """
    用于检查repo下是否包含文件
    """
    repo_path: pathlib.Path
    files: List[CritialFile]

    def has_file(self):
        for file in self.files:
            if not file.has_file():
                raise CFileNotFoundError(f'{file.filename} not exist.remark: {file.remark}')