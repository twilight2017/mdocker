import pathlib
import shutil
import tempfile
import docker
from docker.errors import BuildError

from mdocker.core.project import Project
from mdocker.core.exceptions import DockerError

"""from_env()会返回从环境变量配置的客户端"""
client = docker.from_env()  # 要与Docker守护进程通信，首先要实例化客户端，使用from_env()通过默认套接字或环境中的配置进行连接


def build(project: Project, project_dir):
    with tempfile.TemporaryDirectory() as tmp_dir:  # tempfile用于生成临时文件或目录
        shutil.copytree(project_dir, tmp_dir, dirs_exist_ok=True)
        tmp_dockerfile_path = pathlib.Path(tmp_dir) / 'Dockerfile'
        if not project.custom_dockerfile:
            shutil.copy(project.dockerfile_path, tmp_dockerfile_path)
            with open(tmp_dockerfile_path, 'a') as fp:
                fp.write('CMD' + str(project.entry_commands))
        try:
            image = client.iamges.build(path=tmp_dir)
        except BuildError as e:
            error_msg = ''
            for line in e.build_log:
                if 'stream' in line:
                    error_msg +=line['stream']
            raise DockerError(error_msg)
