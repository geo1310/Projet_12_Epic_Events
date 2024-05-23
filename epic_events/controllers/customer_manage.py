from rich.console import Console
from rich.table import Table

from ..models.customer import Customer
from ..models.database import Session
from ..views.views import View


class CustomerManage:
    """
    Gère les opérations liées aux clients, telles que l'affichage, la création, la mise à jour et la suppression.
    """

    def __init__(self):
        self.session = Session()
        self.view = View()
        self.console = Console()

    def list(self, arg):

        customers = self.session.query(Customer).all()

        # création du tableau
        table = Table(show_header=True, header_style="bold green")
        # Ajouter des colonnes
        table.add_column("ID", style="dim", width=5)
        table.add_column("Prénom")
        table.add_column("Nom")
        table.add_column("Email")
        table.add_column("Tél")
        table.add_column("Entreprise")
        table.add_column("Email du commercial")
        table.add_column("Date de création")
        table.add_column("Date de modification")

        for customer in customers:

            table.add_row(
                str(customer.Id),
                customer.FirstName,
                customer.LastName,
                customer.Email,
                customer.PhoneNumber,
                customer.Company,
                customer.CommercialRel.Email,
                self.format_date(customer.DateCreated),
                self.format_date(customer.DateLastUpdate),
            )

        # Affiche le tableau
        self.view.display_table(table, "\nListe des Clients")
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
