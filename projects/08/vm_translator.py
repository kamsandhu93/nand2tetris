'''
stack pointer at 0

@0
A=M-1
D=M

gets value at top of the stack and sets it to D
'''


import os

from typing import List
from uuid import uuid4



COMMANDS_WITH_2_ARGS = ['push', 'pop']
COMMANDS_WITH_1_ARG = ['if-goto', 'goto', 'label']

SEGMENT_BASE_MAP = {
    'local': 1,
    'argument': 2,
    'this': 3,
    'that': 4,
}


def code_to_list(code: str) -> List[str]:
    return [line.strip() for line in code.split('\n') if line.strip() and not line.isspace()]


def parse_command(command: str) -> List[str]:

    def remove_comments(line: str) -> str:
        line = line.split('//')[0]
        return line.strip()

    command = remove_comments(command)
    parts = command.split(' ')
    if parts[0] in COMMANDS_WITH_2_ARGS:
        assert len(parts) == 3, f'{parts[0]} requires two args'
    elif parts[0] in COMMANDS_WITH_1_ARG:
        assert len(parts) == 2, f'{parts[0]} requires one arg'
    else:
        assert len(parts) == 1, f'{parts[0]} takes no args, {parts[1:]} were given'

    return parts


def generate_add_code() -> List[str]:
    code = f'''
            @0
            A=M-1
            D=M
            @0
            A=M-1
            A=A-1
            M=D+M
            @0
            M=M-1           
            '''

    return code_to_list(code)


def generate_sub_code() -> List[str]:
    code = '''
            @0
            A=M-1
            D=M
            @0
            A=M-1
            A=A-1
            M=M-D
            @0
            M=M-1           
            '''

    return code_to_list(code)


def generate_neg_code() -> List[str]:
    code = '''
            @0
            A=M-1
            M=-M
           '''
    return code_to_list(code)


def generate_eq_code() -> List[str]:
    jump_uuid = f'jump_{str(uuid4())[:5]}'
    code = f'''
            @0
            A=M-1
            D=M
            @0
            A=M-1
            A=A-1
            D=M-D
            M=-1
            @{jump_uuid}
            D;JEQ
            @0
            A=M-1
            A=A-1
            M=0
            ({jump_uuid})
            @0 
            M=M-1
            '''
    return code_to_list(code)


def generate_gt_code() -> List[str]:
    jump_uuid = f'jump_{str(uuid4())[:5]}'
    code = f'''
            @0
            A=M-1
            D=M
            @0
            A=M-1
            A=A-1
            D=M-D
            M=-1
            @{jump_uuid}
            D;JGT
            @0
            A=M-1
            A=A-1
            M=0
            ({jump_uuid})
            @0 
            M=M-1
            '''
    return code_to_list(code)


def generate_lt_code() -> List[str]:
    jump_uuid = f'jump_{str(uuid4())[:5]}'
    code = f'''
            @0
            A=M-1
            D=M
            @0
            A=M-1
            A=A-1
            D=M-D
            M=-1
            @{jump_uuid}
            D;JLT
            @0
            A=M-1
            A=A-1
            M=0
            ({jump_uuid})
            @0 
            M=M-1
            '''
    return code_to_list(code)


def generate_and_code() -> List[str]:
    code = '''
            @0
            A=M-1
            D=M
            @0
            A=M-1
            A=A-1
            M=D&M
            @0
            M=M-1           
            '''

    return code_to_list(code)


def generate_or_code() -> List[str]:
    code = '''
            @0
            A=M-1
            D=M
            @0
            A=M-1
            A=A-1
            M=D|M
            @0
            M=M-1           
            '''

    return code_to_list(code)


def generate_not_code() -> List[str]:
    code = '''
            @0
            A=M-1
            M=!M
           '''
    return code_to_list(code)


def generate_push_code(segment: str, i: str) -> List[str]:
    i = int(i)
    if segment in SEGMENT_BASE_MAP:
        code = f'''
                @{SEGMENT_BASE_MAP[segment]}
                D=M
                @{i}
                D=D+A
                A=D
                D=M
                @0
                A=M
                M=D
                @0
                M=M+1
                '''
    elif segment == 'constant':
        code = f'''
                @{i}
                D=A
                @0
                A=M
                M=D
                @0
                M=M+1                
                '''
    elif segment == 'temp':
        code = f'''
                @{i}
                D=A
                @5
                A=D+A
                D=M
                @0
                A=M
                M=D
                @0
                M=M+1               
                '''
    elif segment == 'static':
        code = f'''
                @static.{i}
                D=M
                @0
                A=M
                M=D
                @0
                M=M+1               
                '''
    elif segment == 'pointer':
        code = f'''
                @{i}
                D=A
                @3
                A=A+D
                D=M
                @0
                A=M
                M=D
                @0
                M=M+1    
                '''
    else:
        raise ValueError(f'{segment} not supported for push')

    return code_to_list(code)


def generate_pop_code(segment: str, i: str) -> List[str]:
    i = int(i)
    if segment in SEGMENT_BASE_MAP:
        code = f'''
                @{SEGMENT_BASE_MAP[segment]}
                D=M
                @{i}
                D=D+A
                
                @13
                M=D
                
                @0
                A=M-1
                D=M

                @13
                A=M
                M=D
                
                @0
                M=M-1
               '''
    elif segment == 'temp':
        code = f'''
                @5
                D=A
                @{i}
                D=D+A

                @13
                M=D

                @0
                A=M-1
                D=M

                @13
                A=M
                M=D

                @0
                M=M-1
                '''
    elif segment == 'static':
        code = f'''
                @0
                A=M-1
                D=M
                @static.{i}
                M=D
                @0
                M=M-1
                '''
    elif segment == 'pointer':
        code = f'''
                @{i}
                D=A
                @3
                D=A+D

                @13
                M=D

                @0
                A=M-1
                D=M
                
                @13
                A=M
                M=D
                
                @0
                M=M-1                
                '''
    else:
        raise ValueError(f'{segment} not supported for pop')

    return code_to_list(code)


def generate_if_go_to_code(label: str):
    code = f'''
            @0
            A=M-1
            D=M
            @{label}
            D;JGT
            '''
    return code_to_list(code)


def generate_go_to_code(label: str):
    code = f'''
            @{label}
            0
;JMP
            '''
    return code_to_list(code)


def generate_label_code(label: str):
    code = f'''
            ({label})
            '''
    return code_to_list(code)


def generate_call_code():
    pass


def generate_function_code():
    pass


def generate_return_code():
    pass


HACK_COMMAND_GENERATORS = {
    'add': generate_add_code,
    'sub': generate_sub_code,
    'and': generate_and_code,
    'or': generate_or_code,
    'neg': generate_neg_code,
    'not': generate_not_code,
    'gt': generate_gt_code,
    'lt': generate_lt_code,
    'eq': generate_eq_code,
    'push': generate_push_code,
    'pop': generate_pop_code,
    'if-goto': generate_if_go_to_code,
    'goto': generate_go_to_code,
    'label': generate_label_code,
    'call': generate_call_code,
    'function': generate_function_code,
    'return': generate_return_code,
}


def main():
    input_path = \
        '/Users/kamsandhu/Documents/Code/prjoects_non_git/nand2tetris/projects/08/ProgramFlow/BasicLoop'



    if os.path.isdir(input_path):
        files_to_translate = [os.path.join(input_path, file) for file in os.listdir(input_path) if file.endswith('.vm')]
    elif os.path.isfile(input_path) and input_path.endswith('.vm'):
        files_to_translate = [input_path]

    output_lines = []

    # add sys.init to output lines

    for file in files_to_translate:

        with open(file, 'r') as f:
            lines = f.readlines()

        # add something to maerk new file in vm code

        for line in lines:
            if line.startswith('//') or not line or line.isspace():
                continue

            output_lines.append(f'// {line[:-1]}')

            parsed_line = parse_command(line)
            cmd = parsed_line[0]
            code_generator_func = HACK_COMMAND_GENERATORS[cmd]
            output_lines.extend(code_generator_func(*parsed_line[1:]))

    file_name = os.path.basename(input_path)
    file_name_wo_extension = os.path.splitext(file_name)[0]
    with open(f'{file_name_wo_extension}.asm', 'w') as f:
        for line in output_lines:
            f.write(f'{line}\n')


if __name__ == '__main__':
    main()
