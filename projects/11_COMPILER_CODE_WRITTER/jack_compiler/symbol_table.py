from collections import namedtuple
from typing import Optional, Dict

from jack_compiler.constants import Constants

Symbol = namedtuple('Symbol', ['name', 'type', 'kind', 'index'])

class SymbolTable:


    def __init__(self):
        self._class_table: Dict[str, Symbol] = {}
        self._subroutine_table: Dict[str, Symbol] = {}



        self.table_map: Dict[str, Dict[str, Symbol]] = {
            Constants.STATIC: self._class_table,
            Constants.FIELD: self._class_table,
            Constants.ARGUMENT: self._subroutine_table,
            Constants.LOCAL: self._subroutine_table
        }

        self.index_map: Dict[str, Optional[int]] = {
            Constants.STATIC: None,
            Constants.FIELD: None,
            Constants.ARGUMENT: None,
            Constants.LOCAL: None
        }

    def start_subroutine(self) -> None:
        self._subroutine_table.clear()
        self.index_map[Constants.ARGUMENT] = None
        self.index_map[Constants.LOCAL] = None


    def define(self, name: str, type: str, kind: str) -> None:

        try:
            table = self.table_map[kind]
        except KeyError as e:
            raise Exception(f'Accepted kinds: {Constants.STATIC}, {Constants.FIELD}, {Constants.LOCAL}, {Constants.ARGUMENT}. '
                            f'Given : {kind}') from e

        self.index_map[kind] = 0 if self.index_map[kind] is None else self.index_map[kind]

        if name in table:
            raise Exception(f'Variable already exists {name} for {kind}')

        table[name] = Symbol(name, type, kind, self.index_map[kind])
        self.index_map[kind] += 1

    def var_count(self, kind: str) -> int:
        index = self.index_map[kind]
        return index if index is not None else 0

    def _find_symbol(self, name: str) -> Symbol:
        try:
            symbol = self._subroutine_table[name]
        except KeyError:
            try:
                symbol =self._class_table[name]
            except KeyError as e:
                raise SymbolNotFound(f'Sybmol {name} not in any table') from e

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

class SymbolNotFound(Exception):
    pass
