import os

from typing import List

from jack_compiler.constants import Constants
from jack_compiler.jack_tokeniser import JackTokenizer
from jack_compiler.symbol_table import SymbolTable, SymbolNotFound
from jack_compiler.vm_writter import VMWriter


def _set_current_grammar_element(grammar_element: str):
    def wrap(func):
        def wrapped_f(*args, **kwargs):
            self = args[0]
            previous_grammar_element = self._current_grammar_element
            self._current_grammar_element = grammar_element
            result = func(*args, **kwargs)
            self._current_grammar_element = previous_grammar_element
            return result
        return wrapped_f
    return wrap


class CompilationError(Exception):
    pass


class CompilationEngine:

    def __init__(self, input_path: str, output_path: str) -> None:

        self._tokenizer = JackTokenizer(input_path)
        self._vm_writer = VMWriter(output_path)
        self._symbol_table = SymbolTable()

        self._output_list = []
        self._current_grammar_element = None

        self._int_label = 0
        self._class_name = None

        self._compile_class()
        self._vm_writer.close()

    @_set_current_grammar_element(Constants.CLASS)
    def _compile_class(self) -> None:
        self._take_keyword([Constants.CLASS])
        self._class_name = self._take_identifier()
        self._take_symbol('{')
        # ClassVarDec 0 to many
        while self._tokenizer.keyword in [Constants.STATIC, Constants.FIELD]:
            self._compile_class_var_dec()
        # SubroutineDec 0 to many
        while self._tokenizer.keyword in [Constants.CONSTRUCTOR, Constants.FUNCTION, Constants.METHOD]:
            self._compile_subroutine()
        self._take_symbol('}')

    @_set_current_grammar_element(Constants.CLASSVARDEC)
    def _compile_class_var_dec(self) -> None:
        kind = self._take_keyword([Constants.STATIC, Constants.FIELD])
        type = self._take_type()
        name = self._take_identifier()

        self._symbol_table.define(name, type, kind)

        # comma separated list of varnames
        while self._tokenizer.symbol == ',':
            self._take_symbol(',')
            name = self._take_identifier()
            self._symbol_table.define(name, type, kind)
        self._take_symbol(';')

    @_set_current_grammar_element(Constants.SUBROUTINEDEC)
    def _compile_subroutine(self) -> None:
        self._symbol_table.start_subroutine()

        subroutine_type = self._take_keyword([Constants.CONSTRUCTOR, Constants.FUNCTION, Constants.METHOD])
        type = self._take_type(extra_keywords=[Constants.VOID])
        name = self._take_identifier()

        self._take_symbol('(')
        self._compile_parameter_list()
        self._take_symbol(')')

        self._take_symbol('{')
        # varDecs
        while self._tokenizer.keyword == Constants.VAR:
            self._compile_var_dec()

        self._vm_writer.write_function(f'{self._class_name}.{name}', self._symbol_table.var_count(Constants.LOCAL))

        if subroutine_type == Constants.CONSTRUCTOR:
            # allocate memory for obj and assign memory addr to this
            self._vm_writer.write_push(Constants.CONSTANT, self._symbol_table.var_count(Constants.FIELD))
            self._vm_writer.write_call('Memory.alloc', 1)
            self._vm_writer.write_pop(Constants.POINTER, 0)
        elif subroutine_type == Constants.METHOD:
            # init this to point at obj (which is first arg)
            self._symbol_table.define('this', self._class_name, Constants.ARGUMENT)
            self._vm_writer.write_push(Constants.ARGUMENT, 0)
            self._vm_writer.write_pop(Constants.POINTER, 0)

        self._compile_statements()
        self._take_symbol('}')

        if subroutine_type == Constants.CONSTRUCTOR:
            # return the memory adr of the object
            self._vm_writer.write_push(Constants.POINTER, 0)
            self._vm_writer.write_return()


    @_set_current_grammar_element(Constants.PARAMETER_LIST)
    def _compile_parameter_list(self) -> None:
        # Parameter list can be empty
        if self._tokenizer.symbol == ')':
            return

        type = self._take_type()
        name = self._take_identifier()
        self._symbol_table.define(name, type, Constants.ARGUMENT)
        # comma separated list of type, varnames
        while self._tokenizer.symbol == ',':
            self._take_symbol(',')
            type = self._take_type()
            name = self._take_identifier()
            self._symbol_table.define(name, type, Constants.ARGUMENT)

    @_set_current_grammar_element(Constants.VARDEC)
    def _compile_var_dec(self) -> None:
        _ = self._take_keyword([Constants.VAR])
        type = self._take_type()
        name = self._take_identifier()
        self._symbol_table.define(name, type, Constants.LOCAL)

        # comma separated list of varnames
        while self._tokenizer.symbol == ',':
            self._take_symbol(',')
            name = self._take_identifier()
            self._symbol_table.define(name, type, Constants.LOCAL)
        self._take_symbol(';')

    @_set_current_grammar_element(Constants.STATEMENTS)
    def _compile_statements(self) -> None:
        statement_map = {
            Constants.IF: self._compile_if_statement,
            Constants.LET: self._compile_let_statement,
            Constants.WHILE: self._compile_while_statement,
            Constants.DO: self._compile_do_statement,
            Constants.RETURN: self._compile_return_statement
        }
        while self._tokenizer.keyword in statement_map:
            compile_func = statement_map[self._tokenizer.keyword]
            compile_func()

    @_set_current_grammar_element(Constants.IF_STATEMENT)
    def _compile_if_statement(self) -> None:
        self._take_keyword([Constants.IF])
        self._take_symbol('(')
        self._compile_expression()
        self._take_symbol(')')

        self._vm_writer.write_arithmetic('~')
        label_1 = self._get_label(Constants.IF)
        label_2 = self._get_label(Constants.IF)
        self._vm_writer.write_if(label_1)

        self._take_symbol('{')
        self._compile_statements()
        self._take_symbol('}')

        self._vm_writer.write_go_to(label_2)
        self._vm_writer.write_label(label_1)
        # Optional ELSE
        if self._tokenizer.keyword == Constants.ELSE:
            self._take_keyword([Constants.ELSE])
            self._take_symbol('{')
            self._compile_statements()
            self._take_symbol('}')

        self._vm_writer.write_label(label_2)

    @_set_current_grammar_element(Constants.LET_STATEMENT)
    def _compile_let_statement(self) -> None:
        self._take_keyword([Constants.LET])
        var_name = self._take_identifier()
        # Optional [expression]
        if self._tokenizer.symbol == '[':
            self._take_symbol('[')
            self._compile_expression()
            self._take_symbol(']')
            self._write_var('push', var_name)
            self._vm_writer.write_arithmetic('+')

            self._take_symbol('=')
            self._compile_expression()
            self._take_symbol(';')

            self._vm_writer.write_pop(Constants.TEMP, 0)
            self._vm_writer.write_pop(Constants.POINTER, 1)
            self._vm_writer.write_push(Constants.TEMP, 0)
            self._vm_writer.write_pop(Constants.THAT, 0)
        else:
            self._take_symbol('=')
            self._compile_expression()
            self._take_symbol(';')

            self._write_var('pop', var_name)

    @_set_current_grammar_element(Constants.WHILE_STATEMENT)
    def _compile_while_statement(self) -> None:
        label_1 = self._get_label(f'{Constants.WHILE}-START')
        label_2 = self._get_label(f'{Constants.WHILE}-END')

        self._take_keyword([Constants.WHILE])
        self._vm_writer.write_label(label_1)

        self._take_symbol('(')
        self._compile_expression()
        self._take_symbol(')')

        self._vm_writer.write_arithmetic('~')
        self._vm_writer.write_if(label_2)

        self._take_symbol('{')
        self._compile_statements()
        self._take_symbol('}')

        self._vm_writer.write_go_to(label_1)
        self._vm_writer.write_label(label_2)

    @_set_current_grammar_element(Constants.DO_STATEMENT)
    def _compile_do_statement(self) -> None:
        self._take_keyword([Constants.DO])
        self._compile_subroutine_call()
        self._take_symbol(';')
        # void function called, dispose of returned 0
        self._vm_writer.write_pop(Constants.TEMP, 0)

    @_set_current_grammar_element(Constants.RETURN_STATEMENT)
    def _compile_return_statement(self) -> None:
        self._take_keyword([Constants.RETURN])
        if self._tokenizer.symbol != ';':
            self._compile_expression()
        else:
             self._vm_writer.write_push(Constants.CONSTANT, 0)
        self._take_symbol(';')
        self._vm_writer.write_return()

    @_set_current_grammar_element(Constants.EXPRESSION_LIST)
    def _compile_expression_list(self) -> int:
        if self._tokenizer.symbol == ')':
            return 0

        n_args = 1

        self._compile_expression()
        while self._tokenizer.symbol == ',':
            self._take_symbol(',')
            self._compile_expression()
            n_args += 1

        return n_args

    @_set_current_grammar_element(Constants.EXPRESSION)
    def _compile_expression(self) -> None:
        self._compile_term()
        while self._tokenizer.symbol in ['+', '-', '*', '/', '&', '|', '<', '>', '=']: #TODO use this list
            symbol = self._tokenizer.symbol
            self._take_symbol(self._tokenizer.symbol)
            self._compile_term()
            self._vm_writer.write_arithmetic(symbol)

    @_set_current_grammar_element(Constants.TERM)
    def _compile_term(self) -> None:
        if self._tokenizer.token_type == Constants.INTVAL:
           _int =  self._take_intval()
           self._vm_writer.write_push(Constants.CONSTANT, int(_int))

        elif self._tokenizer.token_type == Constants.STRINGVAL:
            string = self._take_strval()
            self._vm_writer.write_push(Constants.CONSTANT, len(string))
            self._vm_writer.write_call('String.new', 1)

            for char in string:
                self._vm_writer.write_push(Constants.CONSTANT, ord(char))
                self._vm_writer.write_call('String.appendChar', 2)

        elif self._tokenizer.token_type == Constants.KEYWORD:
            keyword = self._take_keyword([Constants.TRUE, Constants.FALSE, Constants.NULL, Constants.THIS])
            if keyword == Constants.TRUE:
                self._vm_writer.write_push(Constants.CONSTANT, 1)
                self._vm_writer.write_arithmetic('~')
            elif keyword in [Constants.FALSE, Constants.NULL]:
                self._vm_writer.write_push(Constants.CONSTANT, 0)
            else:
                self._vm_writer.write_push(Constants.POINTER, 0)
        elif self._tokenizer.token_type == Constants.SYMBOL:
            if self._tokenizer.symbol in ['-', '~']:
                symbol = self._tokenizer.symbol
                self._take_symbol(self._tokenizer.symbol)
                self._compile_term()
                self._vm_writer.write_arithmetic(symbol)
            elif self._tokenizer.symbol == '(':
                self._take_symbol('(')
                self._compile_expression()
                self._take_symbol(')')
            else:
                raise CompilationError(f'Term only accepts (, ~ and - {Constants.SYMBOL}s, given: '
                                       f'{self._tokenizer.symbol}')
        elif self._tokenizer.token_type == Constants.IDENTIFIER:
            name = self._take_identifier()
            if self._tokenizer.symbol in ['(', '.']:
                self._compile_subroutine_call(name)
            elif self._tokenizer.symbol == '[':
                self._write_var('push', name)
                self._take_symbol('[')
                self._compile_expression()
                self._take_symbol(']')
                self._vm_writer.write_arithmetic('+')
                self._vm_writer.write_pop(Constants.POINTER, 1)
                self._vm_writer.write_push(Constants.THAT, 0)
            else:
                self._write_var('push', name)

    @_set_current_grammar_element(Constants.SUBROUTINECALL)
    def _compile_subroutine_call(self, name: str = None) -> None:
        if name is None:
            name = self._take_identifier()

        pushed_obj = True
        if self._tokenizer.symbol == '.':
            self._take_symbol('.')
            var_name = name
            name = name + '.' + self._take_identifier()
            self._take_symbol('(')
            try:
                self._write_var('push', var_name) #  push object adr
            except SymbolNotFound: # its not a var.call, but a library call
                pushed_obj = False

        else:
            self._take_symbol('(')
            name = f'{self._class_name}.{name}'
            self._vm_writer.write_push(Constants.POINTER, 0)

        n_args = self._compile_expression_list()
        self._take_symbol(')')

        n_args = n_args + 1 if pushed_obj else n_args

        self._vm_writer.write_call(name, n_args)

    def _take_type(self, extra_keywords=None) -> str:
        keywords = [Constants.CHAR, Constants.BOOlEAN, Constants.INT]
        if extra_keywords is not None:
            keywords.extend(extra_keywords)

        if self._tokenizer.token_type == Constants.KEYWORD:
            if self._tokenizer.keyword not in keywords:
                raise CompilationError(
                    f'{self._current_grammar_element} type can only be {", ".join(keywords)} keywords, given keyword: '
                    f'{self._tokenizer.keyword}')
            return self._take_keyword(keywords)
        elif self._tokenizer.token_type == Constants.IDENTIFIER:
            return self._take_identifier()
        else:
            raise CompilationError(
                f'{self._current_grammar_element} type must be {Constants.IDENTIFIER} or {Constants.KEYWORD}, given: '
                f'{self._tokenizer.token_type}')


    def _take_symbol(self, symbol: str) -> str:
        if self._tokenizer.token_type != Constants.SYMBOL or self._tokenizer.symbol != symbol:
            raise CompilationError(f'{self._current_grammar_element} expected the {Constants.SYMBOL}: {symbol}, given: '
                                   f'{self._tokenizer.token_type} {self._tokenizer.token}')
        symbol = self._tokenizer.symbol
        self._tokenizer.advance()
        return symbol

    def _take_keyword(self, accepted_keywords: List) -> str:
        if self._tokenizer.token_type != Constants.KEYWORD:
            raise CompilationError(f'{self._current_grammar_element} expected a {Constants.KEYWORD}, given token type '
                                   f'{self._tokenizer.token_type}')

        if self._tokenizer.keyword not in accepted_keywords:
            raise CompilationError(f'{self._current_grammar_element} keyword should be {", ".join(accepted_keywords)}, '
                                   f'given: {self._tokenizer.keyword}')

        keyword = self._tokenizer.keyword
        self._tokenizer.advance()

        return keyword

    def _take_identifier(self) -> str:
        if self._tokenizer.token_type != Constants.IDENTIFIER:
            raise CompilationError(f'{self._current_grammar_element} expected an identifier, given: '
                                   f'{self._tokenizer.token_type} {self._tokenizer.token}')
        identifier = self._tokenizer.identifier
        self._tokenizer.advance()

        return identifier

    def _take_intval(self) -> str:
        if self._tokenizer.token_type != Constants.INTVAL:
            raise CompilationError(f'{self._current_grammar_element} expected an intVal, given: '
                                   f'{self._tokenizer.token_type}')
        int_val = self._tokenizer.int_val
        self._tokenizer.advance()

        return int_val

    def _take_strval(self) -> str:
        if self._tokenizer.token_type != Constants.STRINGVAL:
            raise CompilationError(f'{self._current_grammar_element} expected a strVal, given: '
                                   f'{self._tokenizer.token_type}')
        string_val = self._tokenizer.string_val

        self._tokenizer.advance()

        return string_val

    def _write_var(self, operation: str, name: str) -> None:
        index = self._symbol_table.index_of(name)
        kind = self._symbol_table.kind_of(name)

        map = {'push': self._vm_writer.write_push, 'pop': self._vm_writer.write_pop}
        func = map[operation]

        if kind == 'field':
            func('this', index)
        else:
            func(kind, index)

    def _get_label(self, prefix):
        label =  f'{prefix}_label_{self._int_label}'
        self._int_label += 1
        return label