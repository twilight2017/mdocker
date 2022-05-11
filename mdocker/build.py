import os
import shutil
import subprocess
import tempfile
import docker
from mdocker.project import Project

client = docker.from_env()


def build(project: Project, build_arg: list, args: str):
    project.check_files()  # 首先检查required_files是否都存在
    with tempfile.TemporaryDirectory() as tmp_dir:  # 打开一个临时文件夹
        shutil.copytree(project.project_dir, tmp_dir, dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git/'))  # 将项目文件复制粘贴过去
        shutil.copy(project.dockerfile_path, os.path.join(tmp_dir, 'Dockerfile'))  # 将dockerfile复制粘贴过去
        docker_args =[  # 添加docker参数
            'docker', 'build', '.', '--progress=plain', '--tag',
            f'{project.name}:{project.git_repo.head.object.hexsha}',
            args
        ]

        for arg in build_arg:  # append build参数
            docker_args.append('--build-arg')
            docker_args.append(arg)
        print(' '.join(docker_args))
        """
        subprocess模块可以产生紫禁城，并连接到子进程的标准输入/输出/错误中去，还可以得到子进程的返回值
        当shell=True是，使用shell来执行这个字符串。如果把shell设置为True,指定的命令会在shell里解释执行
        stdout:文件对象
        cwd:设置工作目录
        subprocess.PIPE 一个可以被用于Popen的stdin、stdout和stderr 3个参数的特殊值，表示需要创建一个新的管道
        """
        p = subprocess.Popen(' '.join(docker_args), shell=True, stdout=subprocess.PIPE, cwd=tmp_dir)  # 子进程管理
        for line in iter(p.stdout.readline, b''):
            print(line)
        p.stdout.close()
        p.wait()
        if p.returncode == 0:
            pass