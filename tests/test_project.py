from mdocker.project import Project, InvaildConfiguration
from tests import BaseTestCase


class ProjectTestCase(BaseTestCase):

    def test_key_missing(self):
        # 从conf文件中删除这两个键，查看报错信息是否能正常提示
        for key in ('name', 'project_dir'):
            conf = self.conf_dict.copy()
            conf.pop(key)
            with self.assertRaises(InvaildConfiguration) as e:
                Project(e)
            self.assertIn(key, str(e.exception))  # 在e.exception字符串检查key

        # 在原配置字典中移除这两个键值对
        self.conf_dict.pop('template')
        self.conf_dict.pop('dockerfile')
        with self.assertRaises(InvaildConfiguration) as e:
            Project(self.conf_dict)
            self.assertIn('dockerfile', str(e))

    def test_key_overriding(self):
        self.conf_dict['required_files'] = ['a', 'b', 'c']
        project = Project(self.conf_dict)
        # 判断project实例的required_files字段和传入配置文件的required_files字段是否一致，若一致 则写入成功
        self.assertEqual(project.required_files, self.conf_dict['required_files'])
