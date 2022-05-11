import pathlib

from git.repo import Repo


def clone(url: str, dst: pathlib.Path) -> Repo:
    Repo.clone_from(url, dst)  # 从某个url那里clone到本地某个位置
