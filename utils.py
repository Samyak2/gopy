from colorama import Fore, Style

lines = []


def print_lexer_error(err_str=""):
    print(f"{Fore.RED}ERROR: {err_str}{Style.RESET_ALL}")


def print_error(err_str=""):
    print(f"{Fore.RED}SYNTAX ERROR: {err_str}{Style.RESET_ALL}")


def print_line(lineno):
    print(
        f"{Fore.GREEN}{lineno:>10}:\t{Style.RESET_ALL}",
        lines[lineno - 1].expandtabs(1),
        sep="",
    )


def print_marker(pos, width=1):
    print(
        Fore.YELLOW,
        " " * 10,
        " \t",
        " " * (pos),
        "^" * width,
        Style.RESET_ALL,
        sep="",
    )
