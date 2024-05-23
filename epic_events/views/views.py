import os

from rich.console import Console
from rich.panel import Panel


class View:

    def __init__(self):
        self.console = Console()

    def show_intro(self, user_connected, user_connected_status):

        self.console.print(Panel(
            "[bold underline blue]Bienvenue sur le CRM Epic Events[/bold underline blue]\n"
            f"\nUtilisateur connecté: [bold blue]{user_connected}[/bold blue]"
            f"\nStatus: [bold blue]{user_connected_status}[/bold blue]"
        ))

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

    def display_table(self, table, title):
        """Affichage d'un tableau

        Args:
            table (Table): Données du tableau
            title (str): Titre du tableau ou None
        """
        if title:
            self.console.print(Panel.fit(f"[underline green bold]{title}[/underline green bold]"))

        self.console.print(table)

    def display_green_message(self, message):
        self.console.print("")
        self.console.print(f"[green]{message}[/green]")

    def display_red_message(self, message):
        self.console.print("")
        self.console.print(f"[bold red]{message}[/bold red]")

    def return_choice(self, text, hidden):
        """Pose une question et renvoie la réponse, la saisie de la réponse peut etre cachée ou non.

        Args:
            text (str): Texte à afficher
            hidden (bool): Saisie cachée si True

        Returns:
            str: Réponse
        """
        self.console.print("")
        answer = self.console.input(f"{text}", password=hidden)
        return answer

    def invalid_choice(self):
        """affiche choix invalide"""
        self.console.print("\nChoix invalide. Veuillez réessayer.\n")

    def prompt_wait_enter(self):
        """Pause de l'affichage, Attente de la touche Entrée"""
        self.console.print()
        self.console.input("[bold]Appuyer sur Entrée[/bold]")
        return True

    def clear_screen(self):
        # detecte le systeme d exploitation
        os_name = os.name
        if os_name == "nt":  # Windows
            os.system("cls")
        elif os_name == "posix":  # Mac, Linux, Unix
            os.system("clear")
