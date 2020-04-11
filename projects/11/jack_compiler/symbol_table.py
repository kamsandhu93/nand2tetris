from collections import namedtuple
from typing import Optional, Dict

from jack_compiler.constants import Constants

Symbol = namedtuple('Symbol', ['name', 'type', 'kind', 'index'])

class SymbolTable:

    def __init__(self):
        self._class_table: Dict[str, Symbol] = {}
        self._subroutine_table: Dict[str, Symbol] = {}

        self._static_index: Optional[int] = None
        self._field_index: Optional[int] = None
        self._arg_index: Optional[int] = None
        self._var_index: Optional[int] = None

        self.table_map: Dict[str, Dict[str, Symbol]] = {Constants.STATIC: self._class_table,
                     Constants.FIELD: self._class_table,
                     Constants.ARG: self._subroutine_table,
                     Constants.VAR: self._subroutine_table}

        self.index_map: Dict[str, Optional[int]] = {Constants.STATIC: self._static_index,
                     Constants.FIELD: self._field_index,
                     Constants.ARG: self._arg_index,
                     Constants.VAR: self._var_index}

    def start_subroutine(self) -> None:
        self._subroutine_table = {}
        self._arg_index = None
        self._var_index = None


    def define(self, name: str, type: str, kind: str) -> None:

        try:
            table = self.table_map[kind]
            index = self.index_map[kind]
        except KeyError as e:
            raise Exception(f'Accepted kinds: {Constants.STATIC}, {Constants.FIELD}, {Constants.VAR}, {Constants.ARG}. '
                            f'Given : {kind}') from e

        index = 0 if index is None else index

        table[name] = Symbol(name, type, kind, index)
        index += 1

    def var_count(self, kind: str) -> int:
        index = self.index_map[kind]
        return index + 1 if index is not None else 0

    def _find_symbol(self, name: str) -> Symbol:
        try:
            symbol = self._subroutine_table[name]
        except KeyError:
            try:
                symbol =self._class_table[name]
            except KeyError as e:
                raise Exception(f'Sybmol {name} not in any table') from e

        return symbol

    def kind_of(self, name: str) ->str:
        symbol = self._find_symbol(name)
        return symbol.kind

    def type_of(self, name: str) -> str:
        symbol = self._find_symbol(name)
        return symbol.type

    def index_of(self, name: str) -> int:
        symbol = self._find_symbol(name)
        return symbol.index
