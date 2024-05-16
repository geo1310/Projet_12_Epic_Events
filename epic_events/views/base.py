import os

from rich.console import Console


class View:

    def __init__(self):
        self.console = Console()

    def display_menu(self, title, menu_list):
        """Affiche le menu d'apres un titre et une liste de menus et renvoie le choix"""
        self.console.print("")
        self.console.print(f"[bold underline]{title}[/bold underline]")
        self.console.print("")
        # affichage du menu
        for menu in menu_list:
            self.console.print(f"\t{menu[0]} - {menu[1]}")
        choice = self.console.input("[bold]\nchoix :[/bold]")
        return choice

    def display_green_message(self, message):
        self.console.print("")
        self.console.print(f"[green]{message}[/green]")

    def display_red_message(self, message):
        self.console.print("")
        self.console.print(f"[bold red]{message}[/bold red]")

    def return_choice(self, text, hidden):
        """pose une question selon un texte caché ou non et renvoie la réponse"""
        self.console.print("")
        answer = self.console.input(f"{text}", password=hidden)
        return answer

    def invalid_choice(self):
        """affiche choix invalide"""
        self.console.print("\nChoix invalide. Veuillez réessayer.\n")

    def prompt_wait_enter(self):
        """Pause de l'affichage, Attente de la touche Entrée"""
        self.console.print()
        self.console.input("Appuyer sur Entrée")
        return True

    def clear_screen(self):
        # detecte le systeme d exploitation
        os_name = os.name
        if os_name == "nt":  # Windows
            os.system("cls")
        elif os_name == "posix":  # Mac, Linux, Unix
            os.system("clear")
