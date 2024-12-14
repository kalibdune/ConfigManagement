import yaml
import sys

MEMORY_SIZE = 1024

class TempBuffer:
    def __init__(self, binary_data: bytes):
        self.binary_data = binary_data
        self.bit_it = 0

    def read(self, bit_width: int) -> int:
        result = 0
        for i in range(bit_width):
            result ^= (((self.binary_data[self.bit_it // 8] >> (self.bit_it % 8)) & 1) << i)
            self.bit_it += 1
        return result

def interpret(binary_path: str, resultult_path: str, memory_range: tuple):
    memory = [0] * MEMORY_SIZE
    register_accumulator = 0

    with open(binary_path, "rb") as f:
        binary_data = f.read()

    buffer = TempBuffer(binary_data)
    i = 0
    while buffer.bit_it < len(binary_data) * 8:  # Используем точное количество бит
        opcode = buffer.read(7)  # Длина opcode
        if opcode == 86:  # LOAD
            operand_b = buffer.read(22)  # Адрес
            operand_c = buffer.read(18)  # Константа
            if buffer.read(17) != 0:  # Проверка на корректность выравнивания
                raise ValueError("Unexpected padding bits.")
            register_accumulator = operand_c
            memory[operand_b] = register_accumulator
            print(f"LOAD: Mem[{operand_b}] = {operand_c}")
        elif opcode == 58:  # READ
            operand_b = buffer.read(22)
            operand_c = buffer.read(18)
            if buffer.read(17) != 0:
                raise ValueError("Unexpected padding bits.")
            register_accumulator = memory[operand_c]
            memory[operand_b] = register_accumulator
            print(f"READ: Mem[{operand_b}] = Mem[{operand_c}] ({memory[operand_c]})")
        elif opcode == 66:  # WRITE
            operand_b = buffer.read(22)
            operand_c = buffer.read(18)
            if buffer.read(17) != 0:
                raise ValueError("Unexpected padding bits.")
            memory[operand_c] = memory[operand_b]
            print(f"WRITE: Mem[{operand_c}] = Mem[{operand_b}] ({memory[operand_b]})")
        elif opcode == 87:  # BITREV
            operand_b = buffer.read(22)
            operand_c = buffer.read(18)
            if buffer.read(17) != 0:
                raise ValueError("Unexpected padding bits.")
            reversed_value = int(bin(memory[operand_c])[2:][::-1], 2)
            memory[operand_b] = reversed_value
            print(f"BITREV: Mem[{operand_b}] = Reverse(Mem[{operand_c}]) ({reversed_value})")
        else:
            raise ValueError(f"Unknown opcode: {opcode}")

    # Записываем данные памяти в YAML файл
    result_data = [{"Address": addr, "Value": memory[addr]} for addr in range(*memory_range)]
    with open(resultult_path, 'w') as yamlfile:
        yaml.dump(result_data, yamlfile, default_flow_style=False)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python script.py <binary_file> <resultult_file> <memory_start> <memory_end>")
        sys.exit(1)

    binary_file = sys.argv[1]
    resultult_file = sys.argv[2]
    try:
        memory_start, memory_end = int(sys.argv[3]), int(sys.argv[4])
    except ValueError:
        print("Memory range must be two integers.")
        sys.exit(1)

    if not (0 <= memory_start < MEMORY_SIZE and 0 <= memory_end <= MEMORY_SIZE and memory_start < memory_end):
        print("Invalid memory range.")
        sys.exit(1)

    interpret(binary_file, resultult_file, (memory_start, memory_end))
