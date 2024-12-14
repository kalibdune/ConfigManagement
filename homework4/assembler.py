import yaml
import sys

# Определяем опкоды для команд
COMMANDS = {
    "LOAD": 86,
    "READ": 58,
    "WRITE": 66,
    "BITREV": 87,
}

class TempBuffer:
    def __init__(self) -> None:
        self.binary_data = bytearray()
        self.bit_size = 0
    
    def write(self, x, bit_width):
        for i in range(bit_width):
            if (self.bit_size + 1) > len(self.binary_data) * 8:
                self.binary_data.append(0)
            self.binary_data[self.bit_size // 8] ^= (((x >> i) & 1) << (self.bit_size % 8))
            self.bit_size += 1

    def align_to_bytes(self):
        while self.bit_size % 8 != 0:
            self.write(0, 1)

def parse_line(line):
    # Игнорируем строки с комментариями и пустые строки
    if line.strip().startswith("#") or not line.strip():
        return None
    parts = line.strip().split()
    command = parts[0].upper()
    if len(parts) < 3:
        raise ValueError(f"Insufficient arguments for command: {line.strip()}")
    operand_b = int(parts[1])
    operand_c = int(parts[2])
    return command, operand_b, operand_c

def process_command(command, operand_b, operand_c, buffer):
    opcode = COMMANDS.get(command)
    if opcode is None:
        raise ValueError(f"Unknown command: {command}")
    
    # Записываем данные в соответствии с форматом
    buffer.write(opcode, 7)      # 7-битный опкод
    buffer.write(operand_b, 22) # 22 бита для operand_b
    buffer.write(operand_c, 18) # 18 бит для operand_c
    buffer.write(0, 17)         # 17 бит для выравнивания

def assemble(input_path, binary_path, log_path):
    buffer = TempBuffer()

    # Считываем и обрабатываем строки из входного файла
    with open(input_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        parsed = parse_line(line)
        if parsed is not None:
            command, operand_b, operand_c = parsed
            process_command(command, operand_b, operand_c, buffer)

    # Выравниваем данные до целых байтов
    buffer.align_to_bytes()

    # Сохраняем бинарные данные
    with open(binary_path, "wb") as f:
        f.write(buffer.binary_data)

    # Логируем команды в YAML
    log_assembly(input_path, log_path)

def log_assembly(input_file, log_file):
    log_data = []
    with open(input_file, 'r') as infile:
        for line in infile:
            parsed = parse_line(line)
            if parsed is not None:
                command, operand_b, operand_c = parsed
                log_data.append({"Command": command, "Operand_B": operand_b, "Operand_C": operand_c})
    
    # Сохраняем лог в формате YAML
    with open(log_file, 'w') as yamlfile:
        yaml.dump(log_data, yamlfile, default_flow_style=False)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python assemble.py <input_file> <binary_file> <log_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    binary_file = sys.argv[2]
    log_file = sys.argv[3]
    assemble(input_file, binary_file, log_file)
