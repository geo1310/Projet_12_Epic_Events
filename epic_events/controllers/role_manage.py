from rich.console import Console
from rich.table import Table

from ..models.database import Session
from ..models.role import Role
from ..views.base import View


class RoleManage:

    def __init__(self):
        self.session = Session()
        self.view = View()
        self.console = Console()

    def list(self, arg):

        roles = self.session.query(Role).all()

        # création du tableau
        table = Table(show_header=True, header_style="bold")
        # Ajouter des colonnes
        table.add_column("ID", style="dim", width=5)
        table.add_column("Nom")
        table.add_column("r_employee")
        table.add_column("ru_employee")
        table.add_column("crud_employee")
        table.add_column("r_role")
        table.add_column("ru_role")
        table.add_column("crud_role")
        table.add_column("r_customer")
        table.add_column("ru_customer")
        table.add_column("crud_customer")
        table.add_column("r_contract")
        table.add_column("ru_contract")
        table.add_column("crud_contract")
        table.add_column("r_event")
        table.add_column("ru_event")
        table.add_column("crud_event")

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
                str(role.DateCreated),
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
