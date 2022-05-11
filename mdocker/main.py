import argparse
import os.path
import pathlib
import sys

import toml

from mdocker.build import build
from mdocker.project import list_project_templates, get_project_template, Project
from mdocker.exceptions import MDockerError

parser = argparse.ArgumentParser(prog='mdocker')
parser.add_argument('project_dir', help='Local path of the directory containing project files, or a remote git url')
parser.add_argument('--type',
                    help='Project type.Must be set if you need the default Dockfiles and project configuration.',
                    choices=list_project_templates())
parser.add_argument('--dockerfile', help='Path to custom dockerfile', metavar='PATH_TO_DOCKERFILE')
parser.add_argument('--toml',
                    help='Path to toml configuration.Can be ignored if you set the options in command line directly',
                    metavar='PATH_TOTOML_FILE')
parser.add_argument('--name', help='Project name')
parser.add_argument('--required-file', nargs='?', action='append', metavar='FILE_PATH',
                    help="""Required file (relative path to the project directory) for the image to build.
                    If the file does not exist, image building will fail.(Can be set in toml)
                    Set this option multiple times to specify more than one file.""")
parser.add_argument('--use-commit', help='Use a specific git commit, branch or tag.', metavar='GIT_OBJECT')
parser.add_argument('--image-name',
                    help='Specify the name of the docker image.Default is the "PROJECT_NAME:HASH_GIT_COMMIT".')
parser.add_argument('--build-arg', nargs='?', action='append',
                    help="""Build arg to be passed to "docker build --build-arg".
                    MUST BE DOUBLE-QUOTED IF QUOTES ARE NEEDED!
                    Eg. --build-arg ssh_prv_key=\'"$(cat ~/.ssh/id_rsa)"\'""",
                    default=[])

parser.add_argument('--docker-args', help="""Args to be passed as-is to \"docker build\",
Eg. --docker-args \"--progress=tty\"""", default='')


def override_conf(conf: dict, key: str, new_value):
    if key in conf_dict:
        print(f'Overriding {key} ({conf[key]}) with new value {new_value}')
    conf[key] = new_value


if __name__ == '__main__':
    args = parser.parse_args()
    toml_path = args.toml
    default_toml, dockerfile_path = get_project_template(args.type)
    conf_dict={}
    if default_toml:
        conf_dict=toml.load(str(default_toml))

    if toml_path:
        if not os.path.exists(toml_path):
            sys.exit(f"TOML file {toml_path} does not exist.")
        new_conf_dict = toml.load(toml_path)  # 加载toml文件，写入配置文件
        for key, value in new_conf_dict.items():
            override_conf(conf_dict, key, value)
        for key in ('name', 'required_files'):
            override_conf(conf_dict, key, getattr(args, key))  # 根据name和required_files的配置参数，写入配置文件
    else:
        conf_dict = args.__dict__
    if args.dockerfile:  # args.dockerfile是必填参数
        dockerfile_path = args.dockerfile  # 从args中读取dockerfile路径参数
    if not dockerfile_path:
        sys.exit("No dockerfile provided.")
    print(args.build_arg)
    try:
        project = Project(conf_dict, args.project_dir, dockerfile_path)  # 根据输入参数，初始化project对象
        build(project, args.build_arg, args.docker_args)  # 针对项目对象，根据build和docker 参数 构建镜像
    except MDockerError as e:
        sys.exit(str(e))  # 失败的话捕捉错误