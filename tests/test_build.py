import os.path
import shutil
from tempfile import mkdtemp
from unittest import mock
from unittest.mock import MagicMock

from git import Repo

from mdocker.build import build
from mdocker.exceptions import InvaildRepo
from mdocker.project import Project
from tests import BaseTestCase


class BuildTestCase(BaseTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.conf_dict['required_types'] = []
        self.project = Project(self.conf_dict)
        self.tmp_dir = mkdtemp()

    def tearDown(self) -> None:
        super().tearDown()
        shutil.rmtree(self.tmp_dir)

    def test_required_file_missing(self):
        self.project.required_files = ['required.txt']
        with self.assertRaises(InvaildRepo) as e:
            build(self.project, self.tmp_dir)
        self.assertIn('required.txt', str(e.exception))

    @mock.patch('subprocess.call')
    def test_docker_args(self, mocked: MagicMock):
        build(self.project, self.tmp_dir)
        self.assertIn('--build-args ssh_prv_key="$(cat ~/.ssh/known_hosts)"', str(mocked.call_args))

    @mock.patch('subprocess.call')
    def test_build_call(self, mocked: MagicMock):
        repo = Repo(self.temp_git_dir)  # 用暂时git目录创建一个Repo
        build(self.project, self.tmp_dir)
        args = f'docker build . --progress plain --no-cache --tag {self.conf_dict["name"]}:{repo.head.object.hexsha}'
        self.assertIn(args, str(mocked.call_args))

    @mock.patch('subprocess.call')
    def test_entrypoint(self, mocked: MagicMock):
        with open(self.project.dockerfile_path, 'w') as fp:
            fp.write('line1\n')
            fp.write('line2')
        build(self.project, self.tmp_dir)
        dockerfile_path = os.path.join(self.tmp_dir, 'Dockerfile')
        with open(dockerfile_path) as fp:
            self.assertEqual(fp.read(), "line1\nline2\nCMD python manage.py runserver")