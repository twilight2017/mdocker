import os.path
import re
import pathlib
import shutil
from os import PathLike
from pathlib import Path
from tempfile import mkdtemp

from typing import Union, Tuple, Optional
import git
import toml
from mdocker.exceptions import InvaildConfiguration, InvaildRepo

_project_templates_dir = pathlib.Path(__file__).parent / 'templates'
_scheme_matcher = re.compile('^(git|https|http):')


def get_key(toml_dict: dict, key: str, required_type: type = str, allow_none=True):
    keys = key.split('.')
    inner_dict = toml_dict
    key_missing = InvaildConfiguration(f"Config key {key} is missing.")
    while len(keys)>0:
        inner_dict = inner_dict.get(keys.pop(0))  # 栈顶元素出栈
        if not isinstance(inner_dict, dict):
            raise key_missing

    value = inner_dict.get(keys[0])
    if not allow_none and value is None:
        raise key_missing

    if not isinstance(value, required_type):
        raise InvaildConfiguration(f"Config key {key} must be of type {required_type}")

    return value


# Union是联合参数的意思，意味着conf_dict参数既可以是pathlib.Path型也可以是dict型
class Project:
    def __init__(self, conf_dict: Union[pathlib.Path, dict], project_dir: PathLike, dockerfile_path: PathLike = None):
        self.git_temp_dir = None
        self.git_repo: Optional[git.Repo] = None
        self.project_dir = project_dir
        self.dockerfile_path = dockerfile_path
        if isinstance(conf_dict, pathlib.Path):  # conf_dict此时传入的只是toml文件路径
            conf_dict = toml.load(str(conf_dict))
        self.name = get_key(conf_dict, 'name', allow_none=False)
        self.required_files = get_key(conf_dict, 'required_files', list) or []
        try:
            self.get_project_repo()
        except git.exc.InvaildGitRepositoryError:
            raise InvaildRepo(f"{project_dir} is not a valid git repo.") from None

    def get_project_repo(self):
        if not _scheme_matcher.match(str(self.project_dir)):  # 是本地项目而非远程项目
            # project_dir is a local path
            if not os.path.exists(self.project_dir):
                raise InvaildRepo(f"{self.project_dir} is not a vaild git repo.")  # 本地项目不存在时触发InvaildRepo Error
            self.git_repo = git.Repo(self.project_dir)
            return
        self.git_temp_dir = mkdtemp()  # 是远程项目，创建一个临时目录
        self.git_repo = git.Repo.clone_from(self.project_dir, self.git_temp_dir)  # 从某个URL那里clone到本地某个位置

    def check_files(self):
        project_dir = pathlib.Path(self.project_dir)  # 获取项目目录的全部文件
        for file in self.required_files:  # 在required_files对项目目录的全部文件进行检查
            path = project_dir / file
            if not path.exists():
                raise InvaildRepo(f'File "{file}" is required but does not exist in the repo')

    # 递归删除临时文件目录下的子文件和子文件夹
    def __del__(self):
        if self.git_temp_dir:
            shutil.rmtree(self.git_temp_dir)  # 递归删除self.git_temp_dir目录下的所有子文件和子文件夹


def list_project_templates() -> list[str]:  # 获取模板文件夹下的所有.toml设置文件
    conf_files = pathlib.Path(_project_templates_dir).glob('*.toml')
    return [conf.stem for conf in conf_files]


def get_project_template(template_name: str) -> tuple[None, None] | tuple[Path, Path|None]:  # 同时获取配置文件和dockerfile，返回一个元组
    if not template_name:
        return None, None
    templates_dir = pathlib.Path(_project_templates_dir)

    toml_path = templates_dir / f'{template_name}.toml'
    if not toml_path.exists():
        raise InvaildConfiguration(f'Project template "{template_name}" does not exist.')
    dockerfile_path = templates_dir / f'{template_name}.Dockerfile'
    if not dockerfile_path.exists():
        dockerfile_path=None
    return toml_path, dockerfile_path
