from dataclasses import dataclass, field
from tabulate import tabulate
from syntree import Node
from typing import Dict, Tuple, Any


@dataclass
class SymbolInfo:
    """Stores information related to a symbol"""

    depth: int
    lineno: int = None
    type_: str = None
    storage: int = None
    symbol: Node = None
    const: bool = False
    value: Any = None
    uses: list = field(default_factory=list)


class SymbolTable:
    """Stores all identifiers, literals and information
    related to them"""

    def __init__(self):
        self.mapping: Dict[Tuple[str, int], SymbolInfo] = {}
        self.depth = 0

    def add(self, symbol: str) -> SymbolInfo:
        if (symbol, self.depth) in self.mapping:
            return self.mapping[symbol, self.depth]

        new_symbol = SymbolInfo(self.depth)
        self.mapping[symbol, self.depth] = new_symbol

        return new_symbol

    def update_info(self, symbol: str, lineno, type_=None, const=None, value=None):
        sym = self.mapping[symbol, self.depth]
        sym.lineno = lineno
        sym.type_ = type_
        # TODO: infer type from value if not given
        # and set storage appropriately
        # sym.storage = types[type_][1]
        if value is not None:
            sym.value = value

        if const is not None:
            sym.const = const

    def check_exists(self, symbol) -> bool:
        return (symbol, self.depth) in self.mapping

    def is_declared(self, symbol) -> bool:
        return (
            self.check_exists(symbol)
            and self.mapping[symbol, self.depth].lineno is not None
        )

    def get_if_exists(self, symbol) -> SymbolInfo:
        return self.mapping.get((symbol, self.depth), None)

    def __str__(self):
        return str(
            tabulate(
                [
                    [
                        key[0],
                        key[1],
                        value.lineno,
                        value.type_,
                        value.storage,
                        value.value,
                        value.uses,
                    ]
                    for key, value in self.mapping.items()
                ],
                headers=[
                    "Symbol",
                    "Depth",
                    "Line No.",
                    "Type",
                    "Storage",
                    "Value",
                    "Uses",
                ],
                tablefmt="fancy_grid",
            )
        )
