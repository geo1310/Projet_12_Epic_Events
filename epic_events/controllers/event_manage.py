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

    def list(self, arg):
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
            if event.EmployeeSupport:
                employee_support = event.EmployeeSupport.FirstName

            table.add_row(
                str(event.Id),
                event.Title,
                event.Notes,
                event.Location,
                str(event.Attendees),
                event.Contract.Title,
                employee_support,
                self.format_date(event.DateStart),
                self.format_date(event.DateEnd),
                self.format_date(event.DateCreated),
            )

        # Affiche le tableau
        self.view.display_table(table, "\nListe des Evènements")
        self.view.prompt_wait_enter()

    def create(self, arg):
        # TODO
        pass

    def update(self, arg):
        # TODO
        pass

    def delete(self, arg):
        # TODO
        pass

    def format_date(self, date):
        if date:
            return date.strftime("%d/%m/%Y")
        return None
