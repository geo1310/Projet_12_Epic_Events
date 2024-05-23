from rich.console import Console
from rich.table import Table

from ..models.database import Session
from ..models.employee import Employee
from ..views.views import View


class EmployeeManage:
    """
    Gère les opérations liées aux employés, telles que l'affichage, la création, la mise à jour et la suppression.
    """

    def __init__(self):
        self.session = Session()
        self.view = View()
        self.console = Console()

    def list(self, arg):

        employees = self.session.query(Employee).all()

        # création du tableau
        table = Table(show_header=True, header_style="bold green")
        # Ajouter des colonnes
        table.add_column("ID", style="dim", width=5)
        table.add_column("Prénom")
        table.add_column("Nom")
        table.add_column("Email")
        table.add_column("Status")
        table.add_column("Client(s)")
        table.add_column("Evènements(s)")
        table.add_column("Date de création")

        for employee in employees:

            customer_list = []
            for customer in employee.CustomersRel:
                customer_list.append(customer.FirstName)

            event_list = []
            for event in employee.EventsRel:
                event_list.append(event.Title)

            table.add_row(
                str(employee.Id),
                employee.FirstName,
                employee.LastName,
                employee.Email,
                employee.RoleRel.RoleName,
                str(customer_list),
                str(event_list),
                self.format_date(employee.DateCreated),
            )

        # Affiche le tableau
        self.view.display_table(table, "\nListe des Employés")
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
