import tkinter as tk
import xml.etree.ElementTree as ET
from zipfile import ZipFile
from pathlib import Path
import re


class Node:
    
    
    def __init__(self, name: str, is_dir: bool = False):
        self.name = name  
        self.is_dir = is_dir  
        self.children = {}  

    def add_child(self, child_node):
        
        self.children[child_node.name] = child_node

    def get_child(self, name):
        
        return self.children.get(name)

    def has_children(self):
        
        return bool(self.children)


class App:
    
    
    cur_dir: str = "/"  
    
    def __init__(self, config_path: str) -> None:
        self._load_config(config_path)  
        self._open_fs()  
        self.root_node = self._build_tree()  
        self._gui_setup()  

    def __del__(self) -> None:
        if self.fs:  # Проверяем, что Zip открыт
            self.fs.close()

    def _open_fs(self) -> None:
        
        self.fs = ZipFile(Path(self.config["file_system_path"]).absolute(), 'a')

    def _build_tree(self) -> Node:
        
        root = Node("/", is_dir=True)  
        file_list = self.fs.namelist()  

        for file_path in file_list:
            parts = file_path.strip("/").split("/")  
            current_node = root  

            for idx, part in enumerate(parts):
                is_dir = (idx != len(parts) - 1)  
                if part not in current_node.children:
                    new_node = Node(part, is_dir=is_dir)
                    current_node.add_child(new_node)
                current_node = current_node.get_child(part)

        return root

    def _dfs_tree(self, node: Node, prefix: str = "") -> str:
        
        tree_str = f"{prefix}{node.name}/\n" if node.is_dir else f"{prefix}{node.name}\n"
        
        sorted_children = sorted(node.children.values(), key=lambda n: (not n.is_dir, n.name))
        for idx, child in enumerate(sorted_children):
            connector = "|__ " if idx == len(sorted_children) - 1 else "|-- "
            tree_str += self._dfs_tree(child, prefix + (connector if idx == len(sorted_children) - 1 else "│   "))
        
        return tree_str

    def _tree_cmd(self, arg: list) -> str:
        
        path = self.cur_dir if not arg else arg[0]
        node = self._find_node_by_path(path.strip("/").split("/"))
        if node:
            return self._dfs_tree(node)
        return "Directory not found."

    def _find_node_by_path(self, parts: list) -> Node:
        
        current_node = self.root_node
        for part in parts:
            if not part:  
                continue
            current_node = current_node.get_child(part)
            if not current_node:
                return None
        return current_node

    def _cd_cmd(self, arg: list):
        if not arg:
            return ""

        if arg[0] == "/":
            # Переход в корень
            self.cur_dir = "/"
        
        elif arg[0] == "..":
            # Переход на уровень выше
            if self.cur_dir != "/":
                # Убираем последний каталог из пути
                self.cur_dir = "/".join(self.cur_dir.rstrip("/").split("/")[:-1]) or "/"
        
        elif arg[0] in self.fs.namelist():
            # Переход в указанную директорию, если она существует
            self.cur_dir = arg[0]

        return ""


    def _touch_cmd(self, arg: list) -> str:
        
        if not arg: return ""
        file_name = arg[0].strip("/")
        if not file_name.startswith(self.cur_dir):
            file_path = f"{self.cur_dir.rstrip('/')}/{file_name}"
            file_path = file_path.lstrip('/')
        
        if file_path in self.fs.namelist():
            return ""
        self.fs.writestr(file_path, "some text here")  
        self._add_file_to_tree(file_path)  
        return ""

    def _add_file_to_tree(self, file_path: str) -> None:
        
        parts = file_path.strip("/").split("/")
        current_node = self.root_node

        for idx, part in enumerate(parts):
            is_dir = (idx != len(parts) - 1)
            if part not in current_node.children:
                new_node = Node(part, is_dir=is_dir)
                current_node.add_child(new_node)
            current_node = current_node.get_child(part)

    def _ls_cmd(self, arg: list) -> str:
        
        path = self.cur_dir if not arg else arg[0]
        node = self._find_node_by_path(path.strip("/").split("/"))
        
        if node and node.has_children():
            return '\n'.join(sorted(node.children.keys()))
        return ""

    def _clear_cmd(self, arg: list):
        
        self.text_field.delete("1.0", tk.END)
        return ""

    def _exit_cmd(self, arg: list):
        
        self.__del__()
        exit(0)

    def _cat_cmd(self, arg: list):
        
        if not arg or arg[0].lstrip("/") not in self.fs.namelist(): return ""
        text = self.fs.read(arg[0]).decode("utf-8")
        return text

    def _echo_cmd(self, arg: list):
        
        if not arg: return ""
        return " ".join(arg)

    def _load_config(self, config_path: str) -> None:
        
        tree = ET.parse(config_path)
        root = tree.getroot()
        self.config = {}
        for setting in root.findall('setting'):
            name = setting.get('name')
            value = setting.text
            self.config[name] = value

    def _gui_setup(self):
        
        self.root = tk.Tk("TTY")
        self.text_field = tk.Text(self.root, width=50, height=25)
        self.button = tk.Button(self.root, text="Confirm", command=self._enter_handler)
        self.text_field.pack(pady=10)
        self.button.pack(pady=5)
        self.text_field.bind("<Return>", self._enter_handler)
        self.text_field.insert("1.0", f"Hello {self.config['username']}!\n{self.cur_dir} > ")

    def _enter_handler(self, event=None) -> str:
        
        src_line = self.text_field.get("1.0", tk.END)
        lines = src_line.strip().split("\n")
        self._cmd_exec(lines[-1].split())
        self.text_field.insert(tk.END, f"\n{self.cur_dir} > ")
        return "break"

    def _cmd_exec(self, lines: list[str]) -> bool:
        
        commands = {
            "ls": self._ls_cmd,
            "cd": self._cd_cmd,
            "clear": self._clear_cmd,
            "exit": self._exit_cmd,
            "cat": self._cat_cmd,
            "touch": self._touch_cmd,
            "echo": self._echo_cmd,
            "tree": self._tree_cmd
        }
        if len(lines) < 3:
            return False
        cmd = lines[2]
        if cmd in commands:
            res = commands[cmd](lines[3:])
            self.text_field.insert(tk.END, f"\n{res}")
            return True
        return False

    def start(self):
        
        self.root.mainloop()


if __name__ == "__main__":
    config_path = Path("config.xml").absolute()
    app = App(config_path)
    app.start()
