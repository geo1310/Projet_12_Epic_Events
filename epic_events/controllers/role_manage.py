from datetime import datetime

from rich.console import Console
from rich.table import Table

from ..models.database import Session
from ..models.role import Role
from ..views.views import View


class RoleManage:
    """
    Gère les opérations liées aux permissions, telles que l'affichage, la création, la mise à jour et la suppression.
    """

    def __init__(self):
        self.session = Session()
        self.view = View()
        self.console = Console()

    def list(self, arg):

        roles = self.session.query(Role).all()

        # création du tableau
        table = Table(show_header=True, header_style="bold green")
        # Ajouter des colonnes
        table.add_column("ID", style="dim", width=3)
        table.add_column("Nom")
        table.add_column("r_ employee")
        table.add_column("ru_ employee")
        table.add_column("crud employee")
        table.add_column("r_ role")
        table.add_column("ru_ role")
        table.add_column("crud role")
        table.add_column("r_ customer")
        table.add_column("ru_ customer")
        table.add_column("crud customer")
        table.add_column("r_ contract")
        table.add_column("ru_ contract")
        table.add_column("crud contract")
        table.add_column("r_ event")
        table.add_column("ru_ event")
        table.add_column("crud event")
        table.add_column("Date de création")

        for role in roles:

            table.add_row(
                str(role.Id),
                role.RoleName,
                str(role.Can_r_Employee),
                str(role.Can_ru_Employee),
                str(role.Can_crud_Employee),
                str(role.Can_r_Role),
                str(role.Can_ru_Role),
                str(role.Can_crud_Role),
                str(role.Can_r_Customer),
                str(role.Can_ru_Customer),
                str(role.Can_crud_Customer),
                str(role.Can_r_Contract),
                str(role.Can_ru_Contract),
                str(role.Can_crud_Contract),
                str(role.Can_r_Event),
                str(role.Can_ru_Event),
                str(role.Can_crud_Event),
                self.format_date(role.DateCreated),
            )

        # Affiche le tableau
        self.view.display_table(table, "\nListe des Permissions")
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
