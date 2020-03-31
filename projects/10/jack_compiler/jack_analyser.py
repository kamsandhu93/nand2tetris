from jack_compiler.compilation_engine import CompilationEngine


class JackAnalyser:

    def __init__(self, path):
        # check path is directory
        # set self to path maybve dont need this
        pass

    @staticmethod
    def run(in_path: str, out_path: str):
        # tokeniser = JackTokenizer(path)
        #
        # with open('/Users/kamsandhu/Documents/Code/prjoects_non_git/nand2tetris/projects/10/Square/SquareGame.my.t
        # .xml', 'w') as f:
        #     f.write('<tokens>\n')
        #
        #     while tokeniser.has_more_tokens:
        #         print(f'{tokeniser.token}\t{tokeniser.token_type}')
        #         f.write(f'<{tokeniser.token_type}> {tokeniser.token} </{tokeniser.token_type}>\n')
        #         tokeniser.advance()
        #
        #     f.write('</tokens>')

        CompilationEngine(in_path, out_path)


if __name__ == '__main__':
    path = '/Users/kamsandhu/Documents/Code/prjoects_non_git/nand2tetris/projects/10/ExpressionLessSquare/SquareGame.jack'
    out_path = 'output/test.xml'
    JackAnalyser.run(path, out_path)
