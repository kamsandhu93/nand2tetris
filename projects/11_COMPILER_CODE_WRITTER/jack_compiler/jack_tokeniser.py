import re
from typing import Generator, Optional, Union

from jack_compiler.constants import Constants


class JackTokenizer:

    KEYWORDS = ("class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean",
                "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return")
    SYMBOLS = ("{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~")
    SPACE = ("\n", "\t", " ")

    def __init__(self, path: str) -> None:

        self._token = None
        self._token_type = None
        self.input_char_stream = self._generate_input_char_stream(path)
        self._current_char = None
        self._has_more_tokens = True

        self._iterate_current_char()

        self.advance()

    @property
    def has_more_tokens(self) -> bool:
        return self._has_more_tokens

    @property
    def token(self) -> Union[Optional[str], Optional[int]]:
        return self._token

    @property
    def token_type(self) -> Optional[str]:
        return self._token_type

    @property
    def keyword(self) -> Optional[str]:
        if not self.token_type == Constants.KEYWORD:
            return None
        return self._token

    @property
    def symbol(self) -> Optional[str]:
        if not self.token_type == Constants.SYMBOL:
            return None
        return self._token

    @property
    def identifier(self) -> Optional[str]:
        if not self.token_type == Constants.IDENTIFIER:
            return None
        return self._token

    @property
    def int_val(self) -> Optional[str]:
        if not self.token_type == Constants.INTVAL:
            return None
        return self._token

    @property
    def string_val(self) -> Optional[str]:
        if not self.token_type == Constants.STRINGVAL:
            return None
        return self._token

    @staticmethod
    def _generate_input_char_stream(path: str) -> Generator[str, None, None]:
        with open(path, 'r') as f:
            lines = f.readlines()
            removed_comments_lines = []
            for line in lines:
                code_part = line.split('//')[0]
                removed_comments_lines.append(code_part)

            removed_comments_code = ' '.join(removed_comments_lines)
            multi_line_comment_regex = r'(/\*\*)(.|\n)*?(\*/)'
            removed_multi_line_comment_code = re.sub(multi_line_comment_regex, ' ', removed_comments_code)

        for char in removed_multi_line_comment_code:
            yield char

    def _iterate_current_char(self):
        if self.has_more_tokens:
            self._current_char = next(self.input_char_stream, None)
            if self._current_char is None:
                self._has_more_tokens = False

    def advance(self) -> None:
        if not self.has_more_tokens:
            return

        while self._current_char and self._current_char.isspace():
            self._iterate_current_char()

        if self._current_char == '"':
            string_list = []
            self._iterate_current_char()
            while self._current_char != '"':
                string_list.append(self._current_char)
                self._iterate_current_char()
            string = ''.join(string_list)

            self._token = string
            self._token_type = Constants.STRINGVAL

            self._iterate_current_char()

        elif self._current_char in self.SYMBOLS:
            self._token = self._current_char
            self._token_type = Constants.SYMBOL

            self._iterate_current_char()

        elif self._current_char and self._current_char.isdigit():
            integer_list = []
            while self._current_char and self._current_char.isdigit():
                integer_list.append(self._current_char)
                self._iterate_current_char()
            integer = int(''.join(integer_list))
            self._token = integer
            self._token_type = Constants.INTVAL

        elif self._current_char and self._current_char.isalpha() or self._current_char == '_':
            identifier_or_keyword_list = []
            while self._current_char and self._current_char.isalpha() or self._current_char == '_':
                identifier_or_keyword_list.append(self._current_char)
                self._iterate_current_char()

            identifier_or_keyword = ''.join(identifier_or_keyword_list)
            self._token = identifier_or_keyword

            if identifier_or_keyword in self.KEYWORDS:
                self._token_type = Constants.KEYWORD
            else:
                self._token_type = Constants.IDENTIFIER

        elif self._current_char is None:
            return

        else:
            raise Exception(f'Unable to tokenize {self._current_char}')
