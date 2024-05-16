from rich.console import Console
from rich.table import Table
from ..models.database import Session
from ..views.base import View
from ..models.employee import Employee

class EmployeeManage:
    
    def __init__(self):
        self.session = Session()
        self.view = View()
        self.console = Console()

    def list(self, arg):
        
        employees = self.session.query(Employee).all()

        # création du tableau
        table = Table(show_header=True, header_style="bold")
        # Ajouter des colonnes
        table.add_column("ID", style="dim", width=5)
        table.add_column("Prénom")
        table.add_column("Nom")
        table.add_column("Email")
        table.add_column("Status")
        table.add_column("Client(s)")
        table.add_column("Date de création")

        for employee in employees:
            
            customer_list = []
            for customer in employee.Customers:
                customer_list.append(customer.FirstName)
                
            table.add_row(
                str(employee.Id), 
                employee.FirstName, 
                employee.LastName, 
                employee.Email,
                employee.Role.RoleName,
                str(customer_list),
                str(employee.DateCreated),
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
