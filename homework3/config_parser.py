import sys
import re
import toml

class ConfigParser:
    def __init__(self):
        self.constants = {}

    def parse_value(self, value):
        if re.match(r"^\d+$", value):
            return int(value)
        elif re.match(r"^\[\[.+\]\]$", value):
            return value[2:-2]
        elif re.match(r"^\(\{.+\}\)$", value):
            array_content = value[2:-2]
            return [self.parse_value(elem.strip()) for elem in array_content.split(",")]
        elif re.match(r"\$.+\$", value):
            const = value[1:-1]
            if const in self.constants:
                return self.constants[const]
            raise ValueError(f"undefined constans: {const}")
        else:
            raise ValueError(f"Invalid value: {value}")
    
    def parse(self, text):
        text = self.remove_comments(text)
        self.parse_constants(text)
        config = self.parse_config(text)
        return config


    def remove_comments(self, text):
        return re.sub(r"' .*", "", text)

    def parse_constants(self, text):
        define_pattern = re.compile(r"\(define\s+([_a-z]+)\s+(.+?)\);")
        for match in define_pattern.finditer(text):
            name, value = match.groups()
            self.constants[name] = self.parse_value(value.strip())

    def parse_config(self, text):
        result = {}
        stack = []
        for line in text.split("\n"):
            line = line.strip()
            if line:
                table_name = re.match(r"(.+)\=\>\s*table\(", line)
                if "table" in line and table_name:
                    stack.append(table_name.group(1).strip())
                    continue
                res = result
                for key in stack:
                    res = res.setdefault(key, {})
                if stack:
                    if ")" in line and re.match(r"\s*\)\s*", line):
                        stack.pop()
                        continue
                    key, val = map(lambda x: x.strip(", "), line.split("=>", 1))
                    res[key] = self.parse_value(val)
        return result

    def generate_toml(self, config):
        return toml.dumps(config)

def main():
    if len(sys.argv) != 2:
        print("Usage: python config_parser.py output.toml")
        sys.exit(1)

    output_file = sys.argv[1]
    config_text = sys.stdin.read()

    parser = ConfigParser()
    try:
        config = parser.parse(config_text)
        toml_output = parser.generate_toml(config)
        with open(output_file, 'w') as toml_file:
            toml_file.write(toml_output)
        print(f"Output written to {output_file}")
    except ValueError as e:
        print(f"Syntax error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()