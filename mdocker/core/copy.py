import pathlib
from .dockerfile import Dockerfile


def build():
    copy_to_repo()
    pass


def copy_to_repo():
    # add to backend repo
    # 在仓库下添加Dockerfile
    docker_path = pathlib.Path('Dockerfile')

    # 将Dockerfile_PDM的内容写入DOcker
    docker_path.write_text(Dockerfile.Dockerfile_PDM)