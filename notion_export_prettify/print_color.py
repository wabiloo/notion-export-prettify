# Initialize Colorama (necessary on Windows)
from colorama import init
from colorama import Fore, Style


# Define wrapper functions for each color
def red(text):
    print(f"{Fore.RED}{text}{Style.RESET_ALL}")


def green(text):
    print(f"{Fore.GREEN}{text}{Style.RESET_ALL}")


def blue(text):
    print(f"{Fore.BLUE}{text}{Style.RESET_ALL}")


def orange(text):
    print(rgb(255, 165, 0, text))


def rgb(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text}\033[39m"


init()
