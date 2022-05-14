import os.path
import pathlib
import re
import shutil
from tempfile import mkdtemp
from typing import Union, Optional, List, Any

import git
import toml

from mdocker.exceptions import InvaildConfiguration, InvaildRepo

_project_templates_dir = pathlib.Path(__file__).parent / 'template'  # pathlib.Path(__file__)返回的是mdocker文件夹
_shceme_matcher = re.compile('^(git|https|http):')


def get_key(toml_dict: dict, key: str, required_type: type = str, allow_none=True) -> Optional[Any]:
    keys = key.split('.')
    inner_dict = toml_dict
    key_missing = InvaildConfiguration(f'Config "{key}" is missing.')
    while len(keys) > 1:
        inner_dict = inner_dict.get(keys.pop(0))
        if not isinstance(inner_dict, dict):
            raise key_missing

    value = inner_dict.get(keys[0])
    if not allow_none and value is None:
        raise key_missing

    if value is not None and not isinstance(value, required_type):
        raise InvaildConfiguration(f'Config "{key}" must be of type "{required_type.__name__}"')

    return value


class Project:
    def __init__(self, conf_dict: Union[pathlib.Path, dict]):
        self.git_temp_dir = None
        self.git_repo: Optional[git.Repo] = None
        if isinstance(conf_dict, pathlib):
            # 配置文件是给定路径的话，加载路径所指向的toml文件
            self.conf_dict = toml.load(str(conf_dict))
        self.name = get_key(conf_dict, 'name', allow_none=False)
        self.project_dir = get_key(conf_dict, 'project_dir', allow_none=False)
        self.dockerfile_path = get_key(conf_dict, 'dockerfile', allow_none=False)
        self.entrypoint = get_key(conf_dict, 'entry', allow_none=False)
        self.required_files = get_key(conf_dict, 'required_files', list) or []
        self.docker_args = get_key(conf_dict, 'docker_args') or ''
        try:
            self.get_project_repo()  # 获取项目仓库
        except git.exc.InvalidGitRepositoryError:
            raise InvaildRepo(f"{self.git_repo} is not a valid git repo.") from None

    # 根据项目地址获得项目仓库
    def get_project_repo(self):
        if not _shceme_matcher.match(str(self.project_dir)):  # 项目目录不是url形式给出的
            if not os.path.exists(self.project_dir):
                raise InvaildRepo(f"{self.git_repo} is not a valid repo .")
            self.git_repo = git.Repo(self.project_dir)
            return
        # 是网络地址的话需要为项目创建临时目录
        self.git_temp_dir = mkdtemp()
        self.git_repo = git.Repo.clone_from(self.project_dir, self.git_temp_dir)

    # 检查required files
    def check_files(self):
        project_dir = pathlib.Path(self.project_dir)
        for file in self.required_files:
            path = project_dir / file
            if not path.exists():
                raise InvaildRepo(f'File "{file}" is required but cannot be found in the repo')

    # 删除临时文件夹
    def __del__(self):
        if self.git_temp_dir:
            shutil.rmtree(self.git_temp_dir)


def list_project_tempaltes() -> List[str]:
    conf_files = pathlib.Path(_project_templates_dir).glob('*.toml')
    return [conf.stem for conf in conf_files]


def get_project_template(template_name: str) -> tuple:
    if not template_name:
        return None, None
    templates_dir = pathlib.Path(_project_templates_dir)  # 根据路径名称得到实际路径
    toml_path = templates_dir / f'{template_name}.toml'
    if not toml_path.exists():
        raise InvaildConfiguration(f'Project template "{template_name}" does not exist.')
    dockerfile_path = templates_dir / f'{template_name}.Dockerfile'
    if not dockerfile_path.exists():
        dockerfile_path = None
    return toml_path, dockerfile_path
