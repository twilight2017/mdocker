import re
import pathlib
import shutil
from tempfile import mkdtemp

from typing import Union, Tuple, Optional

import toml
from mdocker.exceptions import InvaildConfiguration, InvaildRepo

_scheme_matcher = re.compile('^(git|https|http):')


def get_key(toml_dict: dict, key: str, required_type: type=str, allow_none=True):
    keys = key.split('.')
    inner_dict = toml_dict
    key_missing = InvaildConfiguration(f"COnfig key {key} is missing.")
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
    def __init__(self, conf_dict: Union[pathlib.Path, dict], project_dir:str, dockerfile_path:pathlib.Path=None):

        if isinstance(conf_dict, pathlib.Path):
            conf_dict = toml.load(str(conf_dict))
        try:
            self.name = get_key(conf_dict, 'name', allow_none=False)
            self.version = get_key(conf_dict, 'version', allow_none=False)
            self.is_backend = get_key(conf_dict, 'is_backend', required_type=bool, allow_none=False)
            self.entry_commands = get_key(conf_dict, 'entry', required_type=list) or []
            self.required_files = get_key(conf_dict, 'required_files', list) or []
            self.dockerfile_path = dockerfile_path
            self.project_dir = project_dir
            self.git_temp_dir = None
        except InvaildConfiguration as e:
            raise InvaildConfiguration(f'Missing config key "{e}"')
        if not all([cmd, str] for cmd in self.entry_commands):
            raise InvaildConfiguration('"entry" must be a list of command strings.')
        self.get_project_dir()

    def get_project_dir(self):
        if not _scheme_matcher.match(self.project_dir):
            # project_dir is a local path
            return
        self.project_dir = mkdtemp()
        self.git_temp_dir = self.project_dir

    def check_files(self):
        project_dir = pathlib.Path(self.project_dir)
        for file in self.required_files:
            path = project_dir / file
            if not path.exists():
                raise InvaildRepo(f'File "{file}" is required but does not exist in the repo')

    def __del__(self):
        if self.git_temp_dir:
            shutil.rmtree(self.git_temp_dir)  # 递归删除self.git_temp_dir目录下的所有子文件和子文件夹


def get_project_template(template_name: str)-> Tuple[pathlib.Path, Optional[pathlib.Path]]:
    import mdocker.templates as p
    projects_dir = pathlib.Path(p.__file__).parent