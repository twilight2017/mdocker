from mdocker.project import register_projects, get_project

from mdocker.docker import build

register_projects()
project = get_project('qms_backend')
build(project, '/Users/harold/PycharmProjects/qms_backend')