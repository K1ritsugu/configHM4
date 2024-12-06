import argparse
import json

def unpack_instruction(code, pc):
    first_byte = code[pc]
    A = first_byte & 0x7

    if A == 2:
        # LOAD_CONST 4 байта
        inst_bytes = code[pc:pc+4]
        val = int.from_bytes(inst_bytes, 'little')
        A = val & 0x7
        B = (val >> 3) & 0x3F
        C = (val >> 9) & 0x1FFFF
        return A,B,C,4
    elif A == 4:
        # LOAD_MEM 5 байт
        inst_bytes = code[pc:pc+5]
        val = int.from_bytes(inst_bytes, 'little')
        A = val & 0x7
        B = (val >> 3) & 0x3F
        C = (val >> 9) & 0x3FFFFFF
        return A,B,C,5
    elif A == 0:
        # STORE_MEM 5 байт
        inst_bytes = code[pc:pc+5]
        val = int.from_bytes(inst_bytes, 'little')
        A = val & 0x7
        B = (val >> 3) & 0x3FFFFFF
        C = (val >> 29) & 0x3F
        return A,B,C,5
    elif A == 3:
        # EQ 2 байта
        inst_bytes = code[pc:pc+2]
        val = int.from_bytes(inst_bytes, 'little')
        A = val & 0x7
        B = (val >> 3) & 0x3F
        C = (val >> 9) & 0x3F
        return A,B,C,2
    else:
        raise ValueError("Unknown instruction A={}".format(A))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, help='Path to input binary file')
    parser.add_argument('-r', '--result', required=True, help='Path to result json file')
    parser.add_argument('--memstart', type=int, required=True, help='Memory start address')
    parser.add_argument('--memend', type=int, required=True, help='Memory end address')
    args = parser.parse_args()

    with open(args.input,'rb') as f:
        code = f.read()

    # Инициализируем виртуальную машину
    registers = [0]*64
    memory = [0]*1024

    # Первый вектор (адреса 100..107):
    vec1 = [10, 20, 30, 40, 50, 60, 70, 80]
    for i, val in enumerate(vec1):
        memory[100+i] = val

    # Второй вектор (адреса 200..207):
    vec2 = [10, 20, 35, 40, 55, 60, 70, 85]
    for i, val in enumerate(vec2):
        memory[200+i] = val

    pc = 0
    code_length = len(code)

    while pc < code_length:
        A,B,C,size = unpack_instruction(code, pc)
        pc += size

        if A == 2: # LOAD_CONST
            registers[B] = C
        elif A == 4: # LOAD_MEM
            if C < 0 or C >= len(memory):
                raise ValueError("Memory access out of range")
            registers[B] = memory[C]
        elif A == 0: # STORE_MEM
            if B < 0 or B >= len(memory):
                raise ValueError("Memory access out of range")
            if C < 0 or C >= len(registers):
                raise ValueError("Register out of range")
            memory[B] = registers[C]
        elif A == 3: # EQ
            if B < 0 or B >= len(registers) or C < 0 or C >= len(registers):
                raise ValueError("Register out of range")
            registers[B] = 1 if registers[B] == registers[C] else 0
        else:
            raise ValueError("Unknown A in interpreter")

    start = args.memstart
    end = args.memend
    if start < 0 or end >= len(memory) or start > end:
        raise ValueError("Invalid memory range")

    result_slice = memory[start:end+1]

    with open(args.result, 'w', encoding='utf-8') as f:
        json.dump(result_slice, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
