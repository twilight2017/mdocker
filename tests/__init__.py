import os.path
import shutil
import subprocess
from tempfile import mkdtemp
from unittest import TestCase
import toml


# 完成测试相关的初始化配置
class BaseTestCase(TestCase):
    def setUp(self) -> None:
        self.conf_dict = toml.load('./use_template.toml')  # 获取配置字典
        self.temp_git_dir = mkdtemp()  # 创建临时文件夹
        subprocess.call('git init && touch dockerfile && git add . && git commit -m "first"', shell=True,
                        cwd=self.temp_git_dir,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
        self.conf_dict['dockerfile'] = os.path.join(self.temp_git_dir, 'dockerfile')
        self.conf_dict['project_dir'] = self.temp_git_dir  # 初始化项目文件夹

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_git_dir)  # 删除临时文件夹，释放资源
