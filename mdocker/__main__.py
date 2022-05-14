import argparse
import shutil
import sys
from tempfile import mkdtemp

import toml

from mdocker.build import build
from mdocker.exceptions import MDockerError
from mdocker.project import get_project_template, Project, get_key

parser = argparse.ArgumentParser(prog='mdocker')
parser.add_argument('toml_path', help='Path to TOML configuration file.')
parser.add_argument('--use-cache', help='IF set, "--no-cache" won\'t be passed to docker build.', action='store_true')


def override_conf(conf: dict, key: str, new_value: str):
    if key in conf and conf[key] != new_value:
        print(f'Overriding {key}={conf[key]} with new value {new_value}')
    conf[key] = new_value  # 更新字典中的值


def cli():
    # 获取输入参数
    args = parser.parse_args()
    conf_dict = toml.load(args.toml_path)  # 从toml文件中获取配置字典
    default_toml, default_dockerfile = get_project_template(get_key(conf_dict, 'template'))