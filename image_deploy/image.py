import argparse
from loguru import logger
import subprocess

logger.add('image_build.log', rotation="500MB")


class Build:
    def __init__(self, build_args):
        self.name = build_args.name
        self.version = build_args.version
        self.upload_path = build_args.upload_path

    def build(self):
        tmp_dir = "."
        docker_cmd = f'docker build -t {self.name}_{self.version} {tmp_dir}'
        logger.info(f"Docker command: {docker_cmd}")
        subprocess.call(docker_cmd, shell=True, cwd=tmp_dir, bufsize=1)

    def upload_to_aliyun(self):
        docker_tag_cmd = f'docker tag {self.name}_{self.version} ' \
                         f'registry.cn-hangzhou.aliyuncs.com/images_manage/{self.name}:{self.version}'
        subprocess.call(docker_tag_cmd, shell=True, bufsize=1)

        docker_push_cmd = f'docker push registry.cn-hangzhou.aliyuncs.com/images_manage/{self.name}:{self.version}'
        subprocess.call(docker_push_cmd, shell=True, bufsize=1)

    def upload_to_center(self):
        if self.upload_path == 'aliyun':
            Build.upload_to_aliyun(self)


def parse_args():
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument("--name", type=str, help='project name')
    parser.add_argument("--version", type=str, help='release tag')
    parser.add_argument("--upload_path", type=str, help='images management center')
    build_args = parser.parse_args()
    logger.info(
        f"project name: {build_args.name}, version: {build_args.version}, upload_path: {build_args.upload_path}")
    return build_args


if __name__ == '__main__':
    # 读取参数
    args = parse_args()

    # 根据Dokcerfile构建镜像
    build_process = Build(args)
    build_process.build()

    # 上传至镜像托管中心
    build_process.upload_to_center()
