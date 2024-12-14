import unittest
from unittest.mock import patch, mock_open
from io import StringIO
from assembler import TempBuffer, assemble, log_assembly, process_command, COMMANDS
import yaml


class TestAssembler(unittest.TestCase):
    def setUp(self):
        self.input_data = (
            "LOAD 0 1\n"
            "LOAD 1 2\n"
            "LOAD 2 3\n"
            "LOAD 3 4\n"
            "LOAD 4 5\n"
            "LOAD 5 6\n"
            "LOAD 6 7\n"
            "LOAD 7 8\n"
            "BITREV 10 0\n"
            "BITREV 11 1\n"
            "BITREV 12 2\n"
            "BITREV 13 3\n"
            "BITREV 14 4\n"
            "BITREV 15 5\n"
            "BITREV 16 6\n"
            "BITREV 17 7\n"
        )
        self.expected_log = [
            {"Command": "LOAD", "Operand_B": 0, "Operand_C": 1},
            {"Command": "LOAD", "Operand_B": 1, "Operand_C": 2},
            {"Command": "LOAD", "Operand_B": 2, "Operand_C": 3},
            {"Command": "LOAD", "Operand_B": 3, "Operand_C": 4},
            {"Command": "LOAD", "Operand_B": 4, "Operand_C": 5},
            {"Command": "LOAD", "Operand_B": 5, "Operand_C": 6},
            {"Command": "LOAD", "Operand_B": 6, "Operand_C": 7},
            {"Command": "LOAD", "Operand_B": 7, "Operand_C": 8},
            {"Command": "BITREV", "Operand_B": 10, "Operand_C": 0},
            {"Command": "BITREV", "Operand_B": 11, "Operand_C": 1},
            {"Command": "BITREV", "Operand_B": 12, "Operand_C": 2},
            {"Command": "BITREV", "Operand_B": 13, "Operand_C": 3},
            {"Command": "BITREV", "Operand_B": 14, "Operand_C": 4},
            {"Command": "BITREV", "Operand_B": 15, "Operand_C": 5},
            {"Command": "BITREV", "Operand_B": 16, "Operand_C": 6},
            {"Command": "BITREV", "Operand_B": 17, "Operand_C": 7},
        ]

    # @patch("builtins.open", new_callable=mock_open)
    # def test_assemble(self, mock_open):
    #     mock_open.return_value.__enter__.return_value = StringIO()
    #     input_file = self.input_data
    #     with open("mock_programm_file.txt", "w") as file:
    #         file.write(input_file)

    #     binary_file = "mock_binary_file"
    #     log_file = "mock_log_file.yaml"
    #     programm_file = "mock_programm_file.txt"

    #     assemble(programm_file, binary_file, log_file)

    #     # Проверяем, что лог записан корректно
    #     mock_open().seek(0)
    #     log_output = yaml.safe_load(mock_open().read())
    #     self.assertEqual(log_output, self.expected_log)

    # @patch("builtins.open", new_callable=mock_open)
    # def test_log_assembly(self, mock_open):
    #     mock_open.return_value.__enter__.return_value = StringIO()
    #     input_file = StringIO(self.input_data)
    #     log_file = "mock_log_file.yaml"

    #     log_assembly(input_file, log_file)

    #     # Проверяем, что лог записан корректно
    #     mock_open().seek(0)
    #     log_output = yaml.safe_load(mock_open().read())
    #     self.assertEqual(log_output, self.expected_log)

    def test_process_command(self):
        buffer = TempBuffer()
        process_command("LOAD", 0, 1, buffer)
        process_command("BITREV", 10, 0, buffer)

        # Проверяем LOAD
        print(buffer.binary_data)
        self.assertEqual(buffer.binary_data[0], COMMANDS["LOAD"])
        self.assertEqual(buffer.binary_data[5:8], (0).to_bytes(3, byteorder='big'))
        self.assertEqual(buffer.binary_data[5:8], (0).to_bytes(3, byteorder='big'))

        # Проверяем BITREVs
        self.assertEqual(buffer.binary_data[5:8], (0).to_bytes(3, byteorder='big'))
        self.assertEqual(buffer.binary_data[5:8], (0).to_bytes(3, byteorder='big'))
    
    def test_programm(self):
        assemble("mock_programm.txt", "mock_out.bin", "mock_log.yaml")
        

if __name__ == "__main__":
    unittest.main()
