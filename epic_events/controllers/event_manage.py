from rich.console import Console
from rich.table import Table

from ..models.database import Session
from ..models.event import Event
from ..views.views import View


class EventManage:
    """
    Gère les opérations liées aux évènements, telles que l'affichage, la création, la mise à jour et la suppression.
    """

    def __init__(self):
        self.session = Session()
        self.view = View()
        self.console = Console()

    def list(self):
        events = self.session.query(Event).all()

        # création du tableau
        table = Table(show_header=True, header_style="bold green")
        # Ajouter des colonnes
        table.add_column("ID", style="dim", width=5)
        table.add_column("Titre")
        table.add_column("Notes")
        table.add_column("location")
        table.add_column("Places")
        table.add_column("Contrat")
        table.add_column("Employé Support")
        table.add_column("Date de début")
        table.add_column("Date de fin")
        table.add_column("Date de création")

        for event in events:

            employee_support = ""
            if event.EmployeeSupportRel:
                employee_support = event.EmployeeSupportRel.FirstName

            table.add_row(
                str(event.Id),
                event.Title,
                event.Notes,
                event.Location,
                str(event.Attendees),
                event.ContractRel.Title,
                employee_support,
                self.format_date(event.DateStart),
                self.format_date(event.DateEnd),
                self.format_date(event.DateCreated),
            )

        # Affiche le tableau
        self.view.display_table(table, "\nListe des Evènements")
        self.view.prompt_wait_enter()

    def create(self):
        # TODO
        pass

    def update(self):
        # TODO
        pass

    def delete(self):
        # TODO
        pass

    def format_date(self, date:str):
        """
        Formate une date en chaîne de caractères au format "JJ/MM/AAAA HH:MN".

        Cette méthode prend un objet date et le formate en une chaîne de caractères
        selon le format "jour/mois/année". Si la date est None, la méthode retourne None.

        Args:
            date: La date à formater.

        Returns:
            str: La date formatée en chaîne de caractères si la date est fournie, None sinon.
        """
        if date:
            return date.strftime("%d/%m/%Y %H:%M")
        return None
