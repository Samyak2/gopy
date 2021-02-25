from colorama import Fore, Style

lines = []


def print_error():
    print(f"{Fore.RED}SYNTAX ERROR:{Style.RESET_ALL}")


def print_line(lineno):
    print(
        f"{Fore.GREEN}{lineno:>10}:\t{Style.RESET_ALL}",
        lines[lineno - 1],
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
