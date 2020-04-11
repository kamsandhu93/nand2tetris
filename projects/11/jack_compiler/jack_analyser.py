import os

from jack_compiler.compilation_engine import CompilationEngine


class JackAnalyser:

    @staticmethod
    def run(in_path: str, out_path: str):
        CompilationEngine(in_path, out_path)


if __name__ == '__main__':
    path = '/Users/kamsandhu/Documents/Code/prjoects_non_git/nand2tetris/projects/11/Average/Main.jack'
    out_path = os.path.splitext(path)[0] + '.vm'

    JackAnalyser.run(path, out_path)
