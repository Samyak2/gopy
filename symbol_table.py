from dataclasses import dataclass, field
from collections import defaultdict
from tabulate import tabulate
from typing import Dict, Optional, List, Any

import utils
from utils import print_marker, print_line, print_error


@dataclass
class TypeInfo:
    """Stores information for a particular type"""

    name: str
    lineno: Optional[int] = None
    col_num: Optional[int] = None
    storage: Optional[int] = None
    eltype: Any = None

    def __str__(self):
        s = f"Type({self.name}"

        if self.lineno is not None:
            s += f", line={self.lineno}"

        if self.col_num is not None:
            s += f", col={self.col_num}"

        if self.storage is not None:
            s += f", storage={self.storage}"

        s += ")"

        return s


class TypeTable:
    """Store information of all types - predefined and user defined"""

    _predefined = {
        # For INT
        "int": 8,
        "int8": 1,
        "int16": 2,
        "int32": 4,
        "int64": 8,
        # For Float
        "float32": 4,
        "float64": 8,
        # For UINT
        "uint": 8,
        "uint8": 1,
        "uint16": 2,
        "uint32": 4,
        "uint64": 8,
        # For Complex
        "complex64": 8,
        "complex128": 16,
        # For Misc
        "byte": 1,
        "bool": 1,
        "rune": 4,
    }

    def __init__(self):
        self.type_map: Dict[str, TypeInfo] = {}

        for typename, storage in self._predefined.items():
            self.add_type(typename, None, None, storage=storage)

        self.add_type("FUNCTION", None, None, None)
        self.add_type("unknown", None, None, None)
        self.add_type("string", None, None, None, eltype="rune")

    def is_defined(self, name: str):
        """Check if a type is defined"""
        return name in self.type_map

    def get_type(self, name: str) -> TypeInfo:
        return self.type_map[name]

    def add_type(self, name: str, lineno, col_num, storage, eltype=None, check=True):
        """Add a new type definition with the details"""

        if check and self.is_defined(name):
            print_error()
            print(f"Re-declaration of type '{name}' at line {lineno}")
            print_line(lineno)

            pos = col_num - 1
            width = len(name)
            print_marker(pos, width)

            other_type = self.get_type(name)
            print(f"{name} previously declared at line {other_type.lineno}")
            print_line(other_type.lineno)

            pos = other_type.col_num - 1
            print_marker(pos, width)

        new_type = TypeInfo(name, lineno, col_num, storage, eltype)

        self.type_map[name] = new_type

    def __str__(self):
        return str(
            tabulate(
                [
                    [
                        symbol.name,
                        symbol.storage,
                        symbol.eltype,
                    ]
                    for _, symbol in self.type_map.items()
                ],
                headers=[
                    "Type Name",
                    "Storage",
                    "Element Type",
                ],
                tablefmt="psql",
            )
        )


@dataclass
class SymbolInfo:
    """Stores information related to a symbol"""

    name: str
    scope_id: str
    lineno: Optional[int] = None
    col_num: Optional[int] = None
    type_: Optional[TypeInfo] = None
    # storage: Optional[int] = None
    # node: Optional[Node] = None
    const: bool = False
    const_flag: bool = False
    value: Any = None
    uses: list = field(default_factory=list)


class SymbolTable:
    """Stores all identifiers, literals and information
    related to them"""

    def __init__(self, type_table: TypeTable):
        self.symbols: List[SymbolInfo] = []
        self.reset_depth()

        self.type_table = type_table

    def reset_depth(self):
        self.stack: List[Dict[str, SymbolInfo]] = [{}]
        self.cur_scope = "1"
        self.depth = 1
        self.scopes_at_depth: Dict[int, int] = defaultdict(lambda: 0)

        self._add_cur_scope_symbols()

        self.scopes_at_depth[0] = 1

    def _add_cur_scope_symbols(self):
        for symbol in self.symbols:
            if symbol.scope_id == self.cur_scope:
                self.stack[-1][symbol.name] = symbol

    def enter_scope(self):
        self.depth += 1
        self.scopes_at_depth[self.depth] += 1
        self.cur_scope += f".{self.scopes_at_depth[self.depth]}"
        self.stack.append({})

        self._add_cur_scope_symbols()

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

    def remove_symbol(self, symbol: SymbolInfo):
        self.symbols.remove(symbol)
        for symtab_ in reversed(self.stack):
            if symbol in symtab_:
                symtab_.pop(symbol.name)

    def get_symbol(self, symbol: str) -> Optional[SymbolInfo]:
        """Finds the symbol in the closest symtab

        Returns None if symbol doesn't exist
        """
        for symtab_ in reversed(self.stack):
            if symbol in symtab_:
                return symtab_[symbol]

    def update_info(
        self, symbol: str, lineno, col_num=None, type_=None, const=None, value=None
    ):
        sym = self.get_symbol(symbol)
        sym.lineno = lineno
        sym.type_ = None
        sym.col_num = col_num
        # TODO: infer type from value if not given
        typename = None
        composite_type = False
        eltype = None

        if type_ is not None:
            # sym.storage = self.storage[type_.data]
            valid_type = True
            typename = ""

            # type_ can sometimes be syntree.Type
            if hasattr(type_, "data") and hasattr(type_, "name"):
                if type_.name == "BasicType":
                    typename = type_.data
                elif type_.name == "ARRAY" or type_.name == "SLICE":
                    typename = type_.typename
                    composite_type = True
                    eltype = type_.eltype
                else:
                    print(f"Unknown node {type_}. Could not determine type")
                    valid_type = False
            elif isinstance(type_, str):
                typename = type_
            else:
                print(f"Could not determine type, issue in code. Found {type_}")
                valid_type = False

            if valid_type:

                if not self.type_table.is_defined(typename):
                    print_error()
                    print(f"Type '{typename}' is not defined at line {lineno}")
                    print_line(lineno)

                    line = utils.lines[lineno]
                    pos = line.find(typename)
                    width = len(typename)

                    print_marker(pos, width)
                else:
                    sym.type_ = self.type_table.get_type(typename)

            # elif composite_type:

            #     self.type_table.add_type(f"{typename}_{eltype}")

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
        self,
        symbol: str,
        lineno: int,
        col_num: int,
        type_=None,
        const=False,
        value=None,
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

            pos = col_num - 1
            width = len(symbol)
            print_marker(pos, width)

            other_sym = self.get_symbol(symbol)
            print(f"{symbol} previously declared at line {other_sym.lineno}")
            print_line(other_sym.lineno)

            pos = other_sym.col_num - 1
            print_marker(pos, width)
        else:
            self.update_info(
                symbol, lineno, col_num=col_num, type_=type_, const=const, value=value
            )

    def check_unused(self):
        func_type = self.type_table.get_type("FUNCTION")

        for symbol in self.symbols:
            if (
                symbol.uses == []
                and symbol.scope_id != "1"
                and symbol.type_ != func_type
            ):
                print_error("Unused variable", kind="ERROR")
                print(
                    f"Variable {symbol.name} is defined at line {symbol.lineno} "
                    "but never used."
                )
                print_line(symbol.lineno)

                pos = symbol.col_num - 1
                width = len(symbol.name)
                print_marker(pos, width)

        if utils.package_name == "main":
            main_fn = self.get_symbol("main")

            if main_fn is None:
                print_error("main is undeclared in package main", kind="ERROR")

                print("main function is not declared in a file with 'main' package")

    def __str__(self):
        return str(
            tabulate(
                [
                    [
                        symbol.name,
                        symbol.scope_id,
                        symbol.lineno,
                        symbol.type_,
                        symbol.const,
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
                    "Const",
                    "Value",
                    "Uses",
                ],
                tablefmt="psql",
            )
        )
