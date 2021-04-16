from colorama import Fore, Style

lines = []
package_name = None


def print_lexer_error(err_str=""):
    print(f"{Fore.RED}ERROR: {err_str}{Style.RESET_ALL}")


def print_error(err_str="", kind="SYNTAX ERROR"):
    print(f"{Fore.RED}{kind}: {err_str}{Style.RESET_ALL}")


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


def print_line_marker_nowhitespace(lineno):
    line = lines[lineno - 1]
    line = line.expandtabs(1)
    leading_spaces = len(line) - len(line.lstrip(" "))
    ending_spaces = len(line) - len(line.rstrip(" "))

    print_line(lineno)
    print_marker(leading_spaces, len(line) - leading_spaces - ending_spaces)
