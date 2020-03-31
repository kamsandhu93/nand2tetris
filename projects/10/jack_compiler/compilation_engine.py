"""
use decorators

"""

from typing import List
from jack_compiler.jack_tokeniser import JackTokenizer
from jack_compiler.constants import Constants


def _add_xml_tags(element_name: str):
    def wrap(func):
        def wrapped_f(*args, **kwargs):
            self = args[0]
            self._add_to_output_list(element_name, self.OPENTAG)
            result = func(*args, **kwargs)
            self._add_to_output_list(element_name, self.CLOSETAG)
            return result
        return wrapped_f
    return wrap

class CompilationError(Exception):
    pass


class CompilationEngine:
    OPENTAG = 'opentag'
    CLOSETAG = 'closetag'
    VALUE = 'value'

    def __init__(self, input_path: str, output_path: str) -> None:
        self._tokenizer = JackTokenizer(input_path)
        self._output_list = []

        self._compile_class()
        self._write_output(output_path, self._output_list)

    @staticmethod
    def _write_output(output_path: str, output_list: List) -> None:
        with open(output_path, 'w') as f:
            f.writelines(output_list)

    def _add_to_output_list(self, string: str, _type: str) -> None:
        if _type == self.OPENTAG:
            self._output_list.append(f'<{string}>')
        elif _type == self.VALUE:
            self._output_list.append(f' {string} ')
        elif _type == self.CLOSETAG:
            self._output_list.append(f'</{string}>')
        else:
            raise Exception(f'Invalid XML type given {_type}')

    def _add_value_to_output_list(self, value: str, _type: str) -> None:
        self._add_to_output_list(_type, self.OPENTAG)
        self._add_to_output_list(value, self.VALUE)
        self._add_to_output_list(_type, self.CLOSETAG)

    @_add_xml_tags(Constants.CLASS)
    def _compile_class(self) -> None:
        self._compile_keyword(Constants.CLASS, [Constants.CLASS])  # KEYWORD CLASS
        self._compile_identifier(Constants.CLASS)  # Class name
        self._compile_specific_symbol(Constants.CLASS, '{')
        # ClassVarDec 0 to many
        while self._tokenizer.keyword in [Constants.STATIC, Constants.FIELD]:
            self._compile_class_var_dec()

        # SubroutineDec 0 to many
        while self._tokenizer.keyword in [Constants.CONSTRUCTOR, Constants.FUNCTION, Constants.METHOD]:
            self._compile_subroutine_dec()

        self._compile_specific_symbol(Constants.CLASS, '}')

    @_add_xml_tags(Constants.CLASSVARDEC)
    def _compile_class_var_dec(self) -> None:
        self._compile_keyword(Constants.CLASSVARDEC, [Constants.STATIC, Constants.FIELD])
        self._compile_type(Constants.CLASSVARDEC)
        self._compile_var_name(Constants.CLASSVARDEC)
        # comma separated list of varnames
        while self._tokenizer.symbol == ',':
            self._add_value_to_output_list(self._tokenizer.symbol, self._tokenizer.token_type)
            self._tokenizer.advance()

            # varName
            self._compile_var_name(Constants.CLASSVARDEC)

        self._compile_specific_symbol(Constants.CLASSVARDEC, ';')

    @_add_xml_tags(Constants.SUBROUTINEDEC)
    def _compile_subroutine_dec(self) -> None:
        self._compile_keyword(Constants.SUBROUTINEDEC, [Constants.CONSTRUCTOR, Constants.FUNCTION, Constants.METHOD])
        self._compile_type(Constants.SUBROUTINEDEC, extra_keywords=[Constants.VOID])
        self._compile_identifier(Constants.SUBROUTINEDEC)
        self._compile_specific_symbol(Constants.SUBROUTINEDEC, '(')
        self._compile_parameter_list()
        self._compile_specific_symbol(Constants.SUBROUTINEDEC, ')')
        self._compile_subroutine_body()

    @_add_xml_tags(Constants.PARAMETER_LIST)
    def _compile_parameter_list(self) -> None:
        # Parameter list can be empty
        if self._tokenizer.symbol == ')':
            return

        self._compile_type(Constants.PARAMETER_LIST)
        self._compile_var_name(Constants.PARAMETER_LIST)
        # comma separated list of type, varnames
        while self._tokenizer.symbol == ',':
            self._add_value_to_output_list(self._tokenizer.symbol, self._tokenizer.token_type)
            self._tokenizer.advance()
            self._compile_type(Constants.PARAMETER_LIST)
            self._compile_var_name(Constants.PARAMETER_LIST)

    @_add_xml_tags(Constants.SUBROUTINEBODY)
    def _compile_subroutine_body(self) -> None:
        self._compile_specific_symbol(Constants.SUBROUTINEBODY, '{')
        # varDecs
        while self._tokenizer.keyword == Constants.VAR:
            self._compile_var_dec()
        self._compile_statements()
        self._compile_specific_symbol(Constants.SUBROUTINEBODY, '}')

    @_add_xml_tags(Constants.VARDEC)
    def _compile_var_dec(self) -> None:
        self._compile_keyword(Constants.VARDEC, [Constants.VAR])
        self._compile_type(Constants.VARDEC)
        # varname comma separated list
        self._compile_var_name(Constants.VARDEC)
        # comma separated list of varnames
        while self._tokenizer.symbol == ',':
            self._add_value_to_output_list(self._tokenizer.symbol, self._tokenizer.token_type)
            self._tokenizer.advance()
            # varName
            self._compile_var_name(Constants.VARDEC)
        self._compile_specific_symbol(Constants.VARDEC, ';')

    @_add_xml_tags(Constants.STATEMENTS)
    def _compile_statements(self) -> None:
        while self._tokenizer.keyword in [Constants.IF, Constants.LET, Constants.WHILE, Constants.DO, Constants.RETURN]:
            if self._tokenizer.keyword == Constants.IF:
                self._compile_if_statement()
            elif self._tokenizer.keyword == Constants.LET:
                self._compile_let_statement()
            elif self._tokenizer.keyword == Constants.WHILE:
                self._compile_while_statement()
            elif self._tokenizer.keyword == Constants.DO:
                self._compile_do_statement()
            elif self._tokenizer.keyword == Constants.RETURN:
                self._compile_return_statement()

    @_add_xml_tags(Constants.IF_STATEMENT)
    def _compile_if_statement(self) -> None:
        self._compile_keyword(Constants.IF_STATEMENT, [Constants.IF])
        self._compile_specific_symbol(Constants.IF_STATEMENT, '(')
        self._compile_expression()
        self._compile_specific_symbol(Constants.IF_STATEMENT, ')')
        self._compile_specific_symbol(Constants.IF_STATEMENT, '{')
        self._compile_statements()
        self._compile_specific_symbol(Constants.IF_STATEMENT, '}')
        # Optional ELSE
        if self._tokenizer.keyword == Constants.ELSE:
            self._compile_keyword(Constants.IF_STATEMENT, [Constants.ELSE])
            self._compile_specific_symbol(Constants.IF_STATEMENT, '{')
            self._compile_statements()
            self._compile_specific_symbol(Constants.IF_STATEMENT, '}')


    @_add_xml_tags(Constants.LET_STATEMENT)
    def _compile_let_statement(self) -> None:
        self._compile_keyword(Constants.LET_STATEMENT, [Constants.LET])
        self._compile_var_name(Constants.LET_STATEMENT)
        # Optional [expression]
        if self._tokenizer.symbol == '[':
            self._compile_specific_symbol(Constants.LET_STATEMENT, '[')
            self._compile_expression()
            self._compile_specific_symbol(Constants.LET_STATEMENT, ']')

        self._compile_specific_symbol(Constants.LET_STATEMENT, '=')
        self._compile_expression()
        self._compile_specific_symbol(Constants.LET_STATEMENT, ';')


    @_add_xml_tags(Constants.WHILE_STATEMENT)
    def _compile_while_statement(self) -> None:
        self._compile_keyword(Constants.WHILE_STATEMENT, [Constants.WHILE])
        self._compile_specific_symbol(Constants.WHILE_STATEMENT, '(')
        self._compile_expression()
        self._compile_specific_symbol(Constants.WHILE_STATEMENT, ')')
        self._compile_specific_symbol(Constants.WHILE_STATEMENT, '{')
        self._compile_statements()
        self._compile_specific_symbol(Constants.WHILE_STATEMENT, '}')

    @_add_xml_tags(Constants.DO_STATEMENT)
    def _compile_do_statement(self) -> None:
        self._compile_keyword(Constants.DO_STATEMENT, [Constants.DO])
        self._compile_subroutine_call()
        self._compile_specific_symbol(Constants.DO_STATEMENT, ';')

    @_add_xml_tags(Constants.RETURN_STATEMENT)
    def _compile_return_statement(self) -> None:
        self._compile_keyword(Constants.RETURN_STATEMENT, [Constants.RETURN])
        if self._tokenizer.symbol != ';':
            self._compile_expression()

        self._compile_specific_symbol(Constants.RETURN_STATEMENT, ';')

    @_add_xml_tags(Constants.EXPRESSION_LIST)
    def _compile_expression_list(self) -> None:
        if self._tokenizer.symbol == ')':
            return

        self._compile_expression()
        while self._tokenizer.symbol == ',':
            self._compile_specific_symbol(Constants.EXPRESSION_LIST, ',')
            self._compile_expression()

    @_add_xml_tags(Constants.EXPRESSION)
    def _compile_expression(self) -> None:
        self._compile_term()
        if self._tokenizer.symbol in ['+', '-']:  #TODO finish adding ops
            self._compile_specific_symbol(Constants.EXPRESSION, self._tokenizer.symbol)
            self._compile_term()

    @_add_xml_tags(Constants.TERM)
    def _compile_term(self) -> None:
        self._compile_var_name(Constants.TERM)

    def _compile_subroutine_call(self):
        self._compile_identifier(Constants.SUBROUTINECALL)
        if self._tokenizer.symbol == '.':
            self._compile_specific_symbol(Constants.SUBROUTINECALL, '.')
            self._compile_identifier(Constants.SUBROUTINECALL)
        self._compile_specific_symbol(Constants.SUBROUTINECALL, '(')
        self._compile_expression_list()
        self._compile_specific_symbol(Constants.SUBROUTINECALL, ')')

    def _compile_var_name(self, name: str) -> None:
        if self._tokenizer.token_type != Constants.IDENTIFIER:
            raise CompilationError(f'{name} varName must be {Constants.IDENTIFIER}, given: '
                                   f'{self._tokenizer.token_type}')
        self._add_value_to_output_list(self._tokenizer.identifier, self._tokenizer.token_type)
        self._tokenizer.advance()

    def _compile_type(self, name: str, extra_keywords=None) -> None:
        keywords = [Constants.CHAR, Constants.BOOlEAN, Constants.INT]
        if extra_keywords is not None:
            keywords.extend(extra_keywords)

        if self._tokenizer.token_type == Constants.KEYWORD:
            if self._tokenizer.keyword not in keywords:
                raise CompilationError(
                    f'{name} type can only be {", ".join(keywords)} keywords, given keyword: '
                    f'{self._tokenizer.keyword}')
            self._add_value_to_output_list(self._tokenizer.keyword, self._tokenizer.token_type)
            self._tokenizer.advance()
        elif self._tokenizer.token_type == Constants.IDENTIFIER:
            self._add_value_to_output_list(self._tokenizer.identifier, self._tokenizer.token_type)
            self._tokenizer.advance()
        else:
            raise CompilationError(
                f'{name} type must be {Constants.IDENTIFIER} or {Constants.KEYWORD}, given: '
                f'{self._tokenizer.token_type}')

    def _compile_specific_symbol(self, name: str, symbol: str) -> None:
        if self._tokenizer.token_type != Constants.SYMBOL or self._tokenizer.symbol != symbol:
            raise CompilationError(f'{name} expected the {Constants.SYMBOL}: {symbol}, given: '
                                   f'{self._tokenizer.token_type} {self._tokenizer._token}')
        self._add_value_to_output_list(self._tokenizer.symbol, self._tokenizer.token_type)
        self._tokenizer.advance()

    def _compile_keyword(self, name: str, accepted_keywords: List) -> None:
        if self._tokenizer.token_type != Constants.KEYWORD:
            raise CompilationError(f'{name} expected {Constants.KEYWORD}, given token type '
                            f'{self._tokenizer.token_type}')

        if self._tokenizer.keyword not in accepted_keywords:
            raise CompilationError(f'{name} keyword should be {", ".join(accepted_keywords)}, given: '
                            f'{self._tokenizer.keyword}')

        self._add_value_to_output_list(self._tokenizer.keyword, self._tokenizer.token_type)
        self._tokenizer.advance()

    def _compile_identifier(self, name: str) -> None:
        if self._tokenizer.token_type != Constants.IDENTIFIER:
            raise CompilationError(f'{name} expected an identifier, given: {self._tokenizer.token_type}')
        self._add_value_to_output_list(self._tokenizer.identifier, self._tokenizer.token_type)
        self._tokenizer.advance()
