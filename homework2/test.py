import subprocess
import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
from main import DependencyVisualizer

class TestDependencyVisualizer(unittest.TestCase):

    def setUp(self):
        self.config = {
            "graphviz_path": "/usr/local/bin/dot",
            "repository_path": "/path/to/repo",
            "tag_name": "v1.0.0"
        }

        self.git_log_output = """\
        abcdef1 abcdef0
        abcdef2 abcdef1
        abcdef3 abcdef2 abcdef1
        """

    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
        "graphviz_path": "/usr/local/bin/dot",
        "repository_path": "/path/to/repo",
        "tag_name": "v1.0.0"
    }))
    def test_load_config(self, mock_file):
        visualizer = DependencyVisualizer('config.json')
        mock_file.assert_called_once_with('config.json', 'r')
        self.assertEqual(visualizer.config, self.config)

    @patch('subprocess.run')
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
        "graphviz_path": "/usr/local/bin/dot",
        "repository_path": "/path/to/repo",
        "tag_name": "v1.0.0"
    }))
    def test_run_git_command(self, mock_file, mock_subprocess_run):
        mock_subprocess_run.return_value = MagicMock(returncode=0, stdout="output", stderr="")
        visualizer = DependencyVisualizer('config.json')
        output = visualizer._run_git_command('log')

        mock_subprocess_run.assert_called_once_with(['git', '-C', '/path/to/repo', 'log'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(output, "output")

    @patch.object(DependencyVisualizer, '_run_git_command')
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
        "graphviz_path": "/usr/local/bin/dot",
        "repository_path": "/path/to/repo",
        "tag_name": "v1.0.0"
    }))
    def test_get_commit_dependencies(self, mock_file, mock_run_git_command):
        mock_run_git_command.return_value = self.git_log_output

        visualizer = DependencyVisualizer('config.json')
        commit_deps = visualizer.get_commit_dependencies()

        expected_deps = {
            "abcdef1": ["abcdef0"],
            "abcdef2": ["abcdef1"],
            "abcdef3": ["abcdef2", "abcdef1"]
        }
        self.assertEqual(commit_deps, expected_deps)

    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
        "graphviz_path": "/opt/homebrew/bin/dot",
        "repository_path": "/path/to/repo",
        "tag_name": "v1.0.0"
    }))
    def test_build_dot(self, mock_file):
        commit_deps = {
            "abcdef1": ["abcdef0"],
            "abcdef2": ["abcdef1"],
            "abcdef3": ["abcdef2", "abcdef1"]
        }

        visualizer = DependencyVisualizer('config.json')
        dot_data = visualizer.build_dot(commit_deps)

        expected_dot = (
            'digraph G {\n'
            '    "abcdef1" -> "abcdef0";\n'
            '    "abcdef2" -> "abcdef1";\n'
            '    "abcdef3" -> "abcdef2";\n'
            '    "abcdef3" -> "abcdef1";\n'
            '}'
        )
        self.assertEqual(dot_data, expected_dot)

    @patch('subprocess.run')
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
        "graphviz_path": "/usr/local/bin/dot",
        "repository_path": "/path/to/repo",
        "tag_name": "v1.0.0"
    }))
    def test_visualize_graph(self, mock_file, mock_subprocess_run):
        visualizer = DependencyVisualizer('config.json')
        dot_data = 'digraph G { "abcdef1" -> "abcdef0"; }'
        visualizer.visualize_graph(dot_data)
        mock_file().write.assert_called_once_with(dot_data)
        # mock_subprocess_run.assert_any_call(
        #     ['/opt/homebrew/bin/dot', '-Tpng', 'graph.dot', '-o', 'output.png'],
        #     check=True
        # )

    @patch('main.DependencyVisualizer.get_commit_dependencies')
    @patch('main.DependencyVisualizer.build_dot')
    @patch('main.DependencyVisualizer.visualize_graph')
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
        "graphviz_path": "/opt/homebrew/bin/dot",
        "repository_path": "/path/to/repo",
        "tag_name": "v1.0.0"
    }))
    def test_run(self, mock_file, mock_visualize_graph, mock_build_dot, mock_get_commit_dependencies):
        visualizer = DependencyVisualizer('config.json')

        mock_get_commit_dependencies.return_value = {"commit1": ["commit0"]}
        mock_build_dot.return_value = 'digraph G { "commit1" -> "commit0"; }'

        visualizer.run()

        mock_get_commit_dependencies.assert_called_once()
        mock_build_dot.assert_called_once_with({"commit1": ["commit0"]})
        mock_visualize_graph.assert_called_once_with('digraph G { "commit1" -> "commit0"; }')

if __name__ == '__main__':
    unittest.main()
