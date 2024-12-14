import json
import subprocess
import os

class DependencyVisualizer:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = {}
        self.load_config()

    def load_config(self):
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)

        self.graphviz_path = self.config.get('graphviz_path')
        self.repo_path = self.config.get('repository_path')
        self.tag_name = self.config.get('tag_name')

    def _run_git_command(self, *args):
        command = ['git', '-C', self.repo_path] + list(args)
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise Exception(f"Git command failed: {' '.join(command)}\nError: {result.stderr}")
        return result.stdout

    def get_commit_dependencies(self):
        log_output = self._run_git_command("log", "--pretty=format:%H %P", f"{self.tag_name}..HEAD")
        commit_deps = {}
        for line in log_output.splitlines():
            parts = line.strip().split()
            if len(parts) < 1:
                continue
            commit_hash = parts[0]
            parents = parts[1:] if len(parts) > 1 else []
            commit_deps[commit_hash] = parents
        return commit_deps

    def build_dot(self, commit_deps):
        dot = ['digraph G {']
        for commit, parents in commit_deps.items():
            for parent in parents:
                dot.append(f'    "{commit}" -> "{parent}";')
        dot.append('}')
        return '\n'.join(dot)

    def visualize_graph(self, dot_data, output_image='output.png'):
        dot_file = 'graph.dot'
        with open(dot_file, 'w') as f:
            f.write(dot_data)

        subprocess.run([self.graphviz_path, '-Tpng', dot_file, '-o', output_image])
        if os.name == 'posix':
            subprocess.run(['open', output_image])
        elif os.name == 'nt':
            os.startfile(output_image)

    def run(self):
        commit_deps = self.get_commit_dependencies()
        dot_data = self.build_dot(commit_deps)
        self.visualize_graph(dot_data)


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python visualize_deps.py <config_path>")
        sys.exit(1)

    config_path = sys.argv[1]
    visualizer = DependencyVisualizer(config_path)
    visualizer.run()
