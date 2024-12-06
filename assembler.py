import argparse
import json


def pack_load_constant(B, C):
    # A=2
    # A:3b = 2 (010)
    # B:6b
    # C:17b
    A = 2
    val = (A & 0x7) | ((B & 0x3F) << 3) | ((C & 0x1FFFF) << 9)
    return val.to_bytes(4, 'little')

def pack_load_from_memory(B, C):
    # A=4
    # A:3b=100, B:6b, C:26b
    A = 4
    val = (A & 0x7) | ((B & 0x3F) << 3) | ((C & 0x3FFFFFF) << 9)
    return val.to_bytes(5, 'little')

def pack_store_to_memory(B, C):
    A = 0
    val = (A & 0x7) | ((B & 0x3FFFFFF) << 3) | ((C & 0x3F) << 29)
    return val.to_bytes(5, 'little')

def pack_eq(B, C):
    A = 3
    val = (A & 0x7) | ((B & 0x3F) << 3) | ((C & 0x3F) << 9)
    return val.to_bytes(2, 'little')

def parse_line(line):
    parts = line.strip().split()
    if not parts:
        return None
    cmd = parts[0].upper()

    if cmd == 'LOAD_CONST':
        B = int(parts[1])
        C = int(parts[2])
        code = pack_load_constant(B, C)
        return {'A':2,'B':B,'C':C,'bytes':code}
    elif cmd == 'LOAD_MEM':
        B = int(parts[1])
        C = int(parts[2])
        code = pack_load_from_memory(B, C)
        return {'A':4,'B':B,'C':C,'bytes':code}
    elif cmd == 'STORE_MEM':
        B = int(parts[1])
        C = int(parts[2])
        code = pack_store_to_memory(B, C)
        return {'A':0,'B':B,'C':C,'bytes':code}
    elif cmd == 'EQ':
        B = int(parts[1])
        C = int(parts[2])
        code = pack_eq(B, C)
        return {'A':3,'B':B,'C':C,'bytes':code}
    else:
        raise ValueError("Unknown command: "+cmd)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, help='Path to input asm file')
    parser.add_argument('-o', '--output', required=True, help='Path to output binary file')
    parser.add_argument('-l', '--log', required=True, help='Path to log json file')
    args = parser.parse_args()

    instructions = []
    with open(args.input, 'r', encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith('#'):
                continue
            instr = parse_line(line)
            if instr:
                instructions.append(instr)

    code_bytes = b''.join(i['bytes'] for i in instructions)

    with open(args.output, 'wb') as f:
        f.write(code_bytes)

    log_list = []
    for i in instructions:
        log_list.append({
            "A": i['A'],
            "B": i['B'],
            "C": i['C']
        })

    with open(args.log, 'w', encoding='utf-8') as f:
        json.dump(log_list, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
