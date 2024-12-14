import unittest
from config_parser import ConfigParser

class TestConfigParser(unittest.TestCase):
    def setUp(self):
        self.parser = ConfigParser()

    def test_parse_simple_constants(self):
        config_text = """
        (define port 8080);
        (define name [[MyApp]]);
        """
        self.parser.parse_constants(config_text)
        self.assertEqual(self.parser.constants['port'], 8080)
        self.assertEqual(self.parser.constants['name'], 'MyApp')

    def test_parse_constants_with_array(self):
        config_text = """
        (define items ({1, 2, 3}));
        """
        self.parser.parse_constants(config_text)
        self.assertEqual(self.parser.constants['items'], [1, 2, 3])

    def test_parse_config(self):
        config_text = """
        (define host [[localhost]]);

        server => table(
            port => 8080,
            name => $host$
        )
        """
        config = self.parser.parse(config_text)
        self.assertEqual(config['server']['port'], 8080)
        self.assertEqual(config['server']['name'], 'localhost')

    def test_nested_config(self):
        config_text = """
        application => table(
            settings => table(
                debug => 1,
                path => [[/usr/local/bin]]
            ),
            version => [[1.0]]
        )
        """
        config = self.parser.parse(config_text)
        self.assertEqual(config['application']['settings']['debug'], 1)
        self.assertEqual(config['application']['settings']['path'], '/usr/local/bin')
        self.assertEqual(config['application']['version'], '1.0')

    def test_invalid_value(self):
        config_text = """
        invalid => table(
            key => &invalid&
        )
        """
        with self.assertRaises(ValueError):
            self.parser.parse(config_text)

    def test_missing_constant(self):
        config_text = """
        app => table(
            name => $missing$
        )
        """
        with self.assertRaises(ValueError):
            self.parser.parse(config_text)

    def test_generate_toml(self):
        config = {
            "server": {
                "port": 8080,
                "host": "localhost"
            },
            "database": {
                "name": "mydb",
                "timeout": 30
            }
        }
        toml_output = self.parser.generate_toml(config)
        expected_toml = """[server]\nport = 8080\nhost = "localhost"\n\n[database]\nname = "mydb"\ntimeout = 30"""
        self.assertEqual(toml_output.strip(), expected_toml.strip())

# Example configurations from different domains
    def test_web_server_config(self):
        config_text = """
        (define server_name [[example.com]]);

        web_server => table(
            port => 80,
            name => $server_name$,
            ssl => 1
        )
        """
        config = self.parser.parse(config_text)
        self.assertEqual(config['web_server']['port'], 80)
        self.assertEqual(config['web_server']['name'], 'example.com')
        self.assertEqual(config['web_server']['ssl'], 1)

    def test_database_config(self):
        config_text = """
        (define db_name [[testdb]]);

        database => table(
            name => $db_name$,
            max_connections => 100,
            timeout => 30
        )
        """
        config = self.parser.parse(config_text)
        self.assertEqual(config['database']['name'], 'testdb')
        self.assertEqual(config['database']['max_connections'], 100)
        self.assertEqual(config['database']['timeout'], 30)

    def test_application_config(self):
        config_text = """
        application => table(
            name => [[TestApp]],
            version => [[2.1]],
            features => ({ [[feature1]], [[feature2]], [[feature3]] })
        )
        """
        config = self.parser.parse(config_text)
        self.assertEqual(config['application']['name'], 'TestApp')
        self.assertEqual(config['application']['version'], '2.1')
        self.assertEqual(config['application']['features'], ['feature1', 'feature2', 'feature3'])

if __name__ == '__main__':
    unittest.main()
