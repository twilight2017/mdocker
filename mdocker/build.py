import os
import shutil
import subprocess

from mdocker.project import Project


def build(project: Project, tmp_dir: str, use_cache=False):
    project.check_files()  # 检查required files
    # copy repo to a tmp directory
    shutil.copytree(project.project_dir, tmp_dir, dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git/'))
    new_dockerfile_path = os.path.join(tmp_dir, 'Dockerfile')
    shutil.copy(project.dockerfile_path, new_dockerfile_path)

    # write entrypoint

    with open(new_dockerfile_path, 'a') as fp:
        fp.write(f'\nCMD {project.entrypoint}')  # 在dcokerfile末端写入entrypoint

    cache_option = '' if use_cache else '--no-cache'

    # prepare arguments
    docker_cmd = f'docker build . --progress plain {cache_option} --tag {project.name}:{project.git_repo.head.object.hexsha}'
    # 添加上配置文件中的docker参数
    docker_cmd += project.docker_args
    print(f"Docker command: {docker_cmd}")
    subprocess.call(docker_cmd, shell=True, cwd=tmp_dir, bufsize=1)