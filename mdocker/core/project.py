import pathlib
import toml  # toml是一个文件解析处理包，主要支持将文件和字符串解析为字典形式并返回
from mdocker.core.exceptions import InvalidTOML, ProjectDoesNotExist


def _toml_relative_path(toml_path: pathlib.Path):
    return '/'.join(toml_path.parts[-3:])


class Project:
    def __init__(self, toml_path: pathlib.Path):
        conf = toml.load(str(toml_path))
        try:
            self.name = conf['name']
            self.project_type = conf['type']
            self.custom_dockerfile = conf['custom_dockerfile']
            self.entry_commands = conf.get('entry', [])
            self.required_files = conf.get('required_files', [])
            self.dockerfile_path = None
        except KeyError as e:
            raise InvalidTOML(f'Missing config key "{e}"', detail=toml_path)

        # python all()函数用于判断给定的可迭代参数iterable中的所有元素是否都为True，如果是则返回True，否则返回False
        if not isinstance(self.entry_commands, list) or not all([isinstance(cmd, str) for cmd in self.entry_commands]):
            raise InvalidTOML('"entry must be a list of command strings"')

        if not isinstance(self.custom_dockerfile, bool):
            raise InvalidTOML(
                f'"custom_dockerfile" must be a bool value'
            )
        if not self.custom_dockerfile and not self.entry_commands:
            raise InvalidTOML('Missing config key "entry". Provide either a custom dockerfile or entry commands')

        # 指定了dockerfile路径的情况
        if self.custom_dockerfile:
            dockerfile_path = toml_path.parent / 'dockerfile'
            if not dockerfile_path.exists():
                msg = _toml_relative_path(dockerfile_path) + \
                    "does not exist. Set custom_dockerfile to false or provide the file"
                raise InvalidTOML(msg)
            self.dockerfile_path = dockerfile_path

        if self.project_type == 'backend':
            self.dockerfile_path = pathlib.Path(__file__).parent.parent / 'dockerfiles/backend.Dockerfile'
        elif self.project_type == 'frontend':
            self.dockerfile_path = pathlib.Path(__file__).parent.parent / 'dockerfiles/frontend.Dockerfile'
        else:
            raise InvalidTOML(f'Invaild project type "{self.project_type}". Vaild values are "backend" or "frontend"',
                              detail=toml_path)


__projects: dict[str, Project] = {}


def register_projects():
    import mdocker.projects as p
    projects_dir = pathlib.Path(p.__file__).parent  # __file__就是当前脚本的运行路径，projects_dir获取的是projects文件夹路径

    # list all dictionaries and find project modules
    for module in projects_dir.glob('**'):
        if module.name == '__pycache__':  # module遍历了core文件夹下的所有文件
            continue
        toml_path = module / 'conf.toml'
        if not toml_path.exists():
            continue
        project = Project(toml_path)
        if project.name in __projects:
            raise InvalidTOML(f'Project "{project.name}" already exists.', detail=toml_path)
        __projects[project.name] = project
    print('Registered projects: ')
    for project in __projects:
        print('\t' + project)


def get_project(name: str):
    project = __projects.get(name)
    if not project:
        raise ProjectDoesNotExist(f'Project "{name}" does not exist. Check your configurations.')
    return project
