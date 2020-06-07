import re
import os

symbols = {
    'SP': 0,
    'LCL': 1,
    'ARG': 2,
    'THIS': 3,
    'THAT': 4,
    'R0': 0,
    'R1': 1,
    'R2': 2,
    'R3': 3,
    'R4': 4,
    'R5': 5,
    'R6': 6,
    'R7': 7,
    'R8': 8,
    'R9': 9,
    'R10': 10,
    'R11': 11,
    'R12': 12,
    'R13': 13,
    'R14': 14,
    'R15': 15,
    'SCREEN': 16384,
    'KBD': 24576
}

COMP_MAP = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "!D": "0001101",
    "!A": "0110001",
    "-D": "0001111",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",
    "M": "1110000",
    "!M": "1110001",
    "-M": "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101"
}

DEST_MAP = {
    None: 0,
    'M': 1,
    'D': 2,
    'MD': 3,
    'A': 4,
    'AM': 5,
    'AD': 6,
    'AMD': 7
}

JUMP_MAP = {
    None: 0,
    'JGT': 1,
    'JEQ': 2,
    'JGE': 3,
    'JLT': 4,
    'JNE': 5,
    'JLE': 6,
    'JMP': 7
}

last_free_memory = 16

def remove_comments(command: str):
    command = command.strip()
    command = command.split('//')[0]
    return command.strip()


def parse_a_instruct(command: str):
    command = command.strip('@')
    global last_free_memory
    if command not in symbols and not command.isdigit():
        symbols[command] = last_free_memory
        last_free_memory += 1
    value = int(command) if command.isdigit() else symbols[command]
    binary = f'0{value:015b}'
    return binary


def parse_c_instruct(command: str):
    if '=' not in command:
        dest = None
    else:
        dest, command = command.split('=')

    if ';' not in command:
        jump = None
        comp = command
    else:
        comp, jump = command.split(';')


    dest_int = DEST_MAP[dest]
    comp_bin = COMP_MAP[comp]
    jump_int = JUMP_MAP[jump]

    dest_bin = f'{dest_int:03b}'
    jump_bin = f'{jump_int:03b}'

    return f'111{comp_bin}{dest_bin}{jump_bin}'


def main():
    file = '/Users/kamsandhu/Documents/Code/prjoects_non_git/nand2tetris/projects/06/pong/Pong.asm'
    with open(file, 'r') as f:
        lines = f.readlines()

    # first pass
    command_count = 0
    for line in lines:
        line = line.strip()
        if not line or line.startswith('//')  or line.isspace():
            continue
        elif line.startswith('('):
            result = re.search('\((.*)\)', line)
            symbol = result.group(1)
            symbols[symbol] = command_count
        else:
            command_count +=1

    output_list = []
    # 2nd pass
    for line in lines:
        print(f'parsing: {line.strip()}')
        line = remove_comments(line)
        if not line or line.startswith('//') or line.startswith('(') or line.isspace():
            continue
        elif line.startswith('@'):
            output_list.append(parse_a_instruct(line))
        else:
            output_list.append(parse_c_instruct(line))

    file_name = os.path.basename(file)
    file_name_wo_extenstion = os.path.splitext(file_name)[0]

    with open(f'{file_name_wo_extenstion}.hack', 'w') as f:
        for line in output_list:
            f.write(line)
            f.write('\n')

if __name__ == '__main__':
    main()






