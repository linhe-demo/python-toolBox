from colorama import Fore, Back, Style, init


class Show:
    def __init__(self, text=None, style=None):
        self.data = str(text)
        self.style = style

    def print(self):
        init(autoreset=True)  # 初始化 colorama，并自动重置颜色和样式

        if self.style == "red":
            print(Fore.RED + self.data)
        elif self.style == "green":
            print(Back.GREEN + self.data)
        elif self.style == "bright":
            print(Style.BRIGHT + self.data)
        elif self.style == "blue":
            print(Fore.BLUE + self.data)
        elif self.style == "cyan":
            print(Fore.CYAN + self.data)
        else:
            print(Style.RESET_ALL)
