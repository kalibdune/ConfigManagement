import unittest
from pathlib import Path
from zipfile import ZipFile
import os
from main import App, Node  


class TestApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        
        cls.test_zip_path = Path("test_fs.zip")
        with ZipFile(cls.test_zip_path, 'w') as zip_fs:
            zip_fs.mkdir("dir1")
            zip_fs.mkdir("dir2")
            zip_fs.writestr("dir1/file1.txt", "Content of file1")
            zip_fs.writestr("dir2/file2.txt", "Content of file2")
            zip_fs.writestr("file3.txt", "Content of file3")

        config_content = f"""
        <settings>
            <setting name="file_system_path">{cls.test_zip_path}</setting>
            <setting name="username">TestUser</setting>
        </settings>
        """
        cls.config_path = Path("test_config.xml")
        cls.config_path.write_text(config_content)
        
        cls.app = App(cls.config_path)  

    @classmethod
    def tearDownClass(cls):
        
        cls.app.__del__()
        cls.test_zip_path.unlink()  
        cls.config_path.unlink()  
    

    def test_ls_cmd(self):
        
        result = self.app._ls_cmd(None)  
        self.assertIn("dir1", result)
        self.assertIn("dir2", result)
        self.assertIn("file3.txt", result)

    def test_cd_cmd(self):
        
        self.app._cd_cmd(["dir1/"])  
        self.assertEqual(self.app.cur_dir, "dir1/")  
        self.app._cd_cmd(["/"])  
        self.assertEqual(self.app.cur_dir, "/")  

    def test_touch_cmd(self):
        
        self.app._touch_cmd(["newfile.txt"])  
        self.assertIn("newfile.txt", self.app.fs.namelist())  
        self.app.__del__()

    def test_cat_cmd(self):
        
        content = self.app._cat_cmd(["dir1/file1.txt"])  
        self.assertEqual(content, "Content of file1")

    def test_tree_cmd(self):
        
        tree_output = self.app._tree_cmd([])  
        self.assertIn("dir1", tree_output)
        self.assertIn("file1.txt", tree_output)
        self.assertIn("file3.txt", tree_output)

    def test_echo_cmd(self):
        
        result = self.app._echo_cmd(["Hello", "World!"])  
        self.assertEqual(result, "Hello World!")

    def test_clear_cmd(self):
        
        self.app.text_field.insert("1.0", "Some text")
        self.app._clear_cmd([])  
        self.assertEqual(self.app.text_field.get("1.0", "end-1c"), "")  

    
    
    
    


if __name__ == "__main__":
    unittest.main()
