import os

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text


class View:

    def __init__(self):
        self.console = Console()

    def show_intro(self, user_connected: str, user_connected_status: str):
        """
        Affiche une introduction avec les informations de l'utilisateur connecté et son statut.

        Cette méthode crée et affiche un texte formaté contenant le nom de l'utilisateur connecté
        et son statut. Le texte est affiché dans un panneau avec un titre stylisé.

        Args:
            user_connected (str): Le nom de l'utilisateur connecté.
            user_connected_status (str): Le statut de l'utilisateur connecté.
        """
        text = Text("", style="")
        text.append("Utilisateur connecté: ")
        text.append(f"{user_connected}", style="bold blue")
        text.append("\nStatus: ")
        text.append(f"{user_connected_status}", style="bold blue")

        self.console.print(Panel(text, title="[bold]Bienvenue sur le CRM Epic Events[/bold]"))

    def display_menu(self, title: str, menu_list: list):
        """
        Affiche un menu avec un titre et une liste d'options, et demande à l'utilisateur de faire un choix.

        Cette méthode affiche un menu formaté dans un panneau avec un titre stylisé. Chaque option du menu
        est affichée avec un numéro et une description. L'utilisateur est invité à entrer son choix, qui est
        ensuite renvoyé par la méthode.

        Args:
            title (str): Le titre du menu.
            menu_list (list): Une liste de tuples, chaque tuple contenant un numéro et une description du menu.

        Returns:
            str: Le choix de l'utilisateur.
        """

        text = Text()
        # affichage du menu
        for menu in menu_list:
            text.append(f"\n\t{menu[0]} - {menu[1]}", style="bold blue")
        text.append("\n")
        self.console.print(Panel(text, title=f"[bold]{title}[/bold]", width=50))
        choice = self.console.input("[bold]\nchoix :[/bold]")
        return choice

    def display_table(self, table, title: str):
        """
        Affiche un tableau (rich Table) dans un panneau avec un titre formaté.

        Cette méthode prend une table et un titre, puis affiche la table dans un panneau.

        Args:
            table (Table): La table à afficher.
            title (str): Le titre du panneau.

        Returns:
            None
        """

        # Afficher le Text dans un panneau pour une meilleure présentation
        panel = Panel.fit(table, title=f"[bold green]{title}[/bold green]")
        self.console.print("\n")
        self.console.print(panel)

    def display_green_message(self, message: str):
        """
        Affiche un message en vert dans la console.

        Args:
            message (str): Le message à afficher en vert.

        Returns:
            None
        """
        self.console.print("")
        self.console.print(f"[green]{message}[/green]")

    def display_red_message(self, message: str):
        """
        Affiche un message en rouge dans la console.

        Args:
            message (str): Le message à afficher en vert.

        Returns:
            None
        """
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
            self.console.print(Panel.fit(panel_text, border_style=f"{color}"))
        else:
            self.console.print(Panel(panel_text, border_style=f"{color}"))

    def return_choice(self, text: str, hidden: bool = False, default: str = None, choices: list = None):
        """Pose une question et renvoie la réponse, la saisie de la réponse peut être cachée ou non.

        Args:
            text (str): Texte à afficher pour la question.
            hidden (bool): Si True, la saisie sera cachée (utile pour les mots de passe). Par défaut False.
            default (str, optional): Valeur par défaut pour la saisie. Si None, il n'y a pas de valeur par défaut. Par défaut None.
            choices (list, optional): Liste des choix possibles pour la réponse. Par défaut None.

        Returns:
            str: Réponse saisie par l'utilisateur.
        """
        self.console.print("")
        answer = Prompt.ask(
            f"{text}",
            console=self.console,
            password=hidden,
            default=default if default is not None else None,
            choices=choices if choices is not None else None,
        )
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
        """
        Efface l'écran de la console.

        Cette méthode détecte le système d'exploitation utilisé et exécute la commande appropriée
        pour effacer l'écran de la console. Sur Windows, elle utilise la commande 'cls' et sur
        les systèmes Unix-like (Mac, Linux, Unix), elle utilise la commande 'clear'.

        Args:
            None

        Returns:
            None
        """

        os_name = os.name
        if os_name == "nt":  # Windows
            os.system("cls")
        elif os_name == "posix":  # Mac, Linux, Unix
            os.system("clear")
