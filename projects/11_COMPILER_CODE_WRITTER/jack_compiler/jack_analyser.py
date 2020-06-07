import os

from jack_compiler.compilation_engine import CompilationEngine


class JackAnalyser:

    @staticmethod
    def run(in_path: str):
        files = []

        if os.path.isfile(in_path):
            files.append(in_path)
        elif os.path.isdir(in_path):
            files_in_dir = os.listdir(in_path)
            files.extend([os.path.join(in_path, file) for file in files_in_dir if file.endswith('.jack')])
        else:
            raise Exception('Path not dir or file')

        for in_file in files:
            out_file = os.path.splitext(in_file)[0] + '.vm'
            CompilationEngine(in_file, out_file)


if __name__ == '__main__':
    path = '/Users/kamsandhu/Documents/Code/prjoects_non_git/nand2tetris/projects/11/Pong'
    JackAnalyser.run(path)
