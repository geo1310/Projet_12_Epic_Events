import os

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt


class View:

    def __init__(self):
        self.console = Console()

    def show_intro(self, user_connected, user_connected_status):
        text = Text("", style="")
        text.append("Utilisateur connecté: ")
        text.append(f"{user_connected}", style="bold blue")
        text.append("\nStatus: ")
        text.append(f"{user_connected_status}", style="bold blue")

        self.console.print(Panel(text, title="[bold]Bienvenue sur le CRM Epic Events[/bold]"))
            

    def display_menu(self, title, menu_list):
        """Affiche le menu d'apres un titre et une liste de menus et renvoie le choix"""
        text = Text()
        # affichage du menu
        for menu in menu_list:
            text.append(f"\n\t{menu[0]} - {menu[1]}", style="bold blue")
        text.append("\n")
        self.console.print(Panel(text, title=f"[bold]{title}[/bold]", width=50))
        choice = self.console.input("[bold]\nchoix :[/bold]")
        return choice

    def display_table(self, table, title):
        """Affichage d'un tableau

        Args:
            table (Table): Données du tableau
            title (str): Titre du tableau ou None
        """
        
        # Afficher le Text dans un panneau pour une meilleure présentation
        panel = Panel.fit(table, title=f"[bold green]{title}[/bold green]")
        self.console.print("\n")
        self.console.print(panel)

        # self.console.print(table)

    def display_green_message(self, message):
        self.console.print("")
        self.console.print(f"[green]{message}[/green]")

    def display_red_message(self, message):
        self.console.print("")
        self.console.print(f"[bold red]{message}[/bold red]")

    def display_title_panel_color_fit(self, title, color="white", fit=False):
        """Affiche un panneau de titre avec une couleur et une taille ajustée optionnelles.

        Args:
            title (str): Le titre à afficher dans le panneau.
            color (str, optional): La couleur du texte du titre. Par défaut "white".
            fit (bool, optional): Indique si le panneau doit s'ajuster à la taille du texte. Par défaut False.
        """
        panel_text = Text(f"{title}", style=f"bold {color}", justify="center")
        self.console.print("\n")

        if fit:
            self.console.print(Panel.fit(panel_text))
        else:
            self.console.print(Panel(panel_text))

    def return_choice(self, text, hidden):
        """Pose une question et renvoie la réponse, la saisie de la réponse peut etre cachée ou non.

        Args:
            text (str): Texte à afficher
            hidden (bool): Saisie cachée si True

        Returns:
            str: Réponse
        """
        self.console.print("")
        styled_text = Text(text, style="bold", justify="center")
        answer = self.console.input(styled_text, password=hidden)
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
