from dataclasses import dataclass, field
from collections import defaultdict
from tabulate import tabulate
from typing import Dict, Any, Optional, List

import utils
from utils import print_marker, print_line, print_error


@dataclass
class SymbolInfo:
    """Stores information related to a symbol"""

    name: str
    scope_id: str
    lineno: Optional[int] = None
    type_: Optional[str] = None
    storage: Optional[int] = None
    # node: Optional[Node] = None
    const: bool = False
    value: Any = None
    uses: list = field(default_factory=list)


class SymbolTable:
    """Stores all identifiers, literals and information
    related to them"""

    def __init__(self):
        self.stack: List[Dict[str, SymbolInfo]] = [{}]
        self.symbols: List[SymbolInfo] = []
        self.cur_scope = "1"
        self.depth = 1
        self.scopes_at_depth: Dict[int, int] = defaultdict(lambda: 0)
        self.scopes_at_depth[0] = 1

    def enter_scope(self):
        self.depth += 1
        self.scopes_at_depth[self.depth] += 1
        self.cur_scope += f".{self.scopes_at_depth[self.depth]}"
        self.stack.append({})

    def leave_scope(self):
        self.depth -= 1
        ind_of_dot = self.cur_scope.rfind(".")
        self.cur_scope = self.cur_scope[:ind_of_dot]
        self.scopes_at_depth[self.depth + 2] = 0
        self.stack.pop()

    def add_if_not_exists(self, symbol: str) -> SymbolInfo:
        if symbol in self.stack[-1]:
            return self.stack[-1][symbol]

        new_symbol = SymbolInfo(symbol, self.cur_scope)

        self.symbols.append(new_symbol)
        self.stack[-1][symbol] = new_symbol

        return new_symbol

    def get_symbol(self, symbol: str) -> Optional[SymbolInfo]:
        """Finds the symbol in the closest symtab

        Returns None if symbol doesn't exist
        """
        for symtab_ in reversed(self.stack):
            if symbol in symtab_:
                return symtab_[symbol]

    def update_info(self, symbol: str, lineno, type_=None, const=None, value=None):
        sym = self.get_symbol(symbol)
        sym.lineno = lineno
        sym.type_ = type_
        # TODO: infer type from value if not given
        # and set storage appropriately
        # sym.storage = types[type_][1]
        if value is not None:
            sym.value = value

        if const is not None:
            sym.const = const

    def exists_in_cur_symtab(self, symbol: str) -> bool:
        return symbol in self.stack[-1]

    def is_declared(self, symbol: str) -> bool:
        for symtab_ in reversed(self.stack):
            if symbol in symtab_:
                if symtab_[symbol].lineno is not None:
                    return True
        return False

    def is_declared_in_cur_symtab(self, symbol: str) -> bool:
        return (
            self.exists_in_cur_symtab(symbol)
            and self.stack[-1][symbol].lineno is not None
        )

    def declare_new_variable(
        self, symbol: str, lineno: int, type_=None, const=False, value=None
    ):
        """Helper function to add symbol to the Symbol Table
        with declaration set to given line number.

        Prints an error if the symbol is already declared at
        current depth.
        """
        if self.is_declared_in_cur_symtab(symbol):
            print_error()
            print(f"Re-declaration of symbol '{symbol}' at line {lineno}")
            print_line(lineno)
            line: str = utils.lines[lineno - 1]
            # TODO: get correct position of token rather than searching
            pos = line.find(symbol)
            width = len(symbol)
            print_marker(pos, width)
            other_sym = self.get_symbol(symbol)
            print(f"{symbol} previously declared at line {other_sym.lineno}")
            print_line(other_sym.lineno)
            line: str = utils.lines[other_sym.lineno - 1]
            pos = line.find(symbol)
            print_marker(pos, width)
        else:
            self.update_info(symbol, lineno, type_=type_, const=const, value=value)

    def __str__(self):
        return str(
            tabulate(
                [
                    [
                        symbol.name,
                        symbol.scope_id,
                        symbol.lineno,
                        symbol.type_,
                        symbol.storage,
                        symbol.value,
                        symbol.uses,
                    ]
                    for symbol in self.symbols
                ],
                headers=[
                    "Symbol",
                    "Scope",
                    "Line No.",
                    "Type",
                    "Storage",
                    "Value",
                    "Uses",
                ],
                tablefmt="fancy_grid",
            )
        )
