from typing import Optional
from rich.console import Console
from rich.table import Table

from app.models.employee import Employee
from app.models.role import Role
from app.utils.sentry_logger import SentryLogger
from app.views.views import View

from .utils_manage import UtilsManage


class EmployeeManage:
    """
    Gère les opérations liées aux employés, telles que l'affichage, la création, la mise à jour et la suppression.
    """

    def __init__(self, session, employee, role):
        self.session = session
        self.view = View()
        self.console = Console()
        self.employee = employee
        self.role = role
        self.user_connected_id = employee.Id
        self.sentry = SentryLogger()
        self.utils = UtilsManage(self.employee)

    def list(self):
        employees = self.utils.filter(self.session, "All", None, Employee)
        table = self.utils.table_create("employee", employees)
        self.view.display_table(table, "Liste des Employés")

    def create(self) -> None:
        """
        Crée un nouvel employé après avoir collecté et validé les informations de l'utilisateur.
        """

        self.view.display_title_panel_color_fit("Création d'un employé", "green")

        # Collecte les informations de l'utilisateur

        first_name = self.view.return_choice("Entrez le prénom de l'employé ( facultatif )", False)
        last_name = self.view.return_choice("Entrez le nom de famille de l'employé ( facultatif )", False)

        # Validation de l'email
        email = self.validation_email()
        if not email:
            return
        self.view.display_green_message("Email validé !")

        # Validation du mot de passe
        password_hash = self.validation_password()
        if not password_hash:
            return
        self.view.display_green_message("Mot de passe validé !")

        # validation du role
        role_id = self.valid_role()
        if not role_id:
            return

        # Instance du nouvel objet Employee
        employee = Employee(
            FirstName=first_name, LastName=last_name, Email=email, PasswordHash=password_hash, RoleId=int(role_id)
        )

        self.utils.valid_oper(self.session, "employee", "create", employee)

    def update(self) -> None:
        """
        Mets à jour les informations d'un employé existant.

        Cette méthode permet de modifier les informations d'un employé en demandant à l'utilisateur
        de saisir un identifiant d'employé, puis de valider les nouvelles informations fournies. Les
        modifications sont affichées pour confirmation avant d'être enregistrées dans la base de données.
        """
        self.view.display_title_panel_color_fit("Modification d'un employé", "yellow")

        # Validation de l'employé à modifier par son Id
        employee = self.utils.valid_id(self.session, Employee, "employé à modifier")
        if not employee:
            return

        # Affichage et confirmation de la modification
        if not self.utils.confirm_table_recap("employee", employee, "Modification", "yellow"):
            return

        self.view.display_title_panel_color_fit("Modification d'un employé", "yellow", True)
        employee.FirstName = self.view.return_choice("Prénom", False, f"{employee.FirstName}")
        employee.LastName = self.view.return_choice("Nom", False, f"{employee.LastName}")
        employee.Email = self.view.return_choice("Email", False, f"{employee.Email}")

        # validation du role
        role_id = self.valid_role(employee.RoleId)

        if not role_id:
            return
        employee.RoleId = role_id

        # Modification du mot de passe
        confirm = self.view.return_choice("Voulez-vous modifier le mot de passe ? (oui/non)", False)
        if confirm == "oui":
            password_hash = self.validation_password()
            if not password_hash:
                return
            self.view.display_green_message("Mot de passe validé !")

            employee.PasswordHash = password_hash

        self.utils.valid_oper(self.session, "employee", "update", employee)

    def delete(self) -> None:
        """
        Supprime un employé existant.

        Cette méthode permet de supprimer un employé en demandant à l'utilisateur
        de saisir un identifiant d'employé, puis de valider la suppression.
        La suppression est affichée pour confirmation avant d'être exécutée.
        """

        self.view.display_title_panel_color_fit("Suppression d'un employé", "red")

        # Validation de l'employé à supprimer par son Id
        employee = self.utils.valid_id(self.session, Employee, "employé à supprimer")
        if not employee:
            return

        self.utils.valid_oper(self.session, "employee", "delete", employee)

    def validation_email(self) -> Optional[str]:
        """
        Valide l'adresse e-mail saisie par l'utilisateur.

        Demande à l'utilisateur de saisir une adresse e-mail et valide son format.
        Si l'adresse e-mail n'est pas valide, affiche un message d'erreur et demande
        de saisir à nouveau l'adresse e-mail. Si l'adresse e-mail est valide, la retourne.

        Returns:
            str: L'adresse e-mail validée.
            None: Si l'utilisateur n'a pas fourni d'adresse e-mail.
        """

        while True:
            email = self.view.return_choice("Entrez l'adresse email ( vide pour annuler )", False)
            if not email:
                return None
            try:
                Employee.validate_email(self, "email", email)
            except ValueError as e:
                self.view.display_red_message(f"Erreur de validation : {e}")
            else:
                return email

    def validation_password(self) -> Optional[str]:
        """
        Valide le mot de passe saisi par l'utilisateur.

        Demande à l'utilisateur de saisir un mot de passe et de le confirmer.
        Si les mots de passe ne correspondent pas ou ne respectent pas les règles de
        validation, affiche un message d'erreur et demande de saisir à nouveau les mots de passe.
        Si le mot de passe est valide, le hash et le retourne.

        Returns:
            str: Le hash du mot de passe validé.
            None: Si l'utilisateur n'a pas fourni de mot de passe.
        """

        while True:
            password = self.view.return_choice("Entrez le mot de passe de l'employé ( vide pour annuler )", True)
            if not password:
                return None
            confirm_password = self.view.return_choice(
                "Confirmez le mot de passe de l'employé ( vide pour annuler )", True
            )
            if not confirm_password:
                return None

            if password == confirm_password:
                try:
                    Employee.validate_password_hash(self, "PasswordHash", password)
                except ValueError as e:
                    self.view.display_red_message(f"Erreur de validation : {e}")
                else:
                    return password
            else:
                self.view.display_red_message("Les mots de passe ne correspondent pas.")

    def valid_role(self, role_default: int = None):
        """
        Affiche un tableau de choix pour les rôles et demande à l'utilisateur de sélectionner un rôle.

        Cette méthode affiche un tableau contenant tous les rôles disponibles et demande à l'utilisateur
        de saisir l'identifiant du rôle souhaité. Si un identifiant par défaut est fourni, il sera proposé par défaut.
        Si l'utilisateur saisit une valeur valide, la méthode retourne l'identifiant du rôle. Sinon, elle retourne None.

        Args:
            role_default (int, optional): Identifiant du rôle par défaut. Défaut à None.

        Returns:
            int: L'identifiant du rôle sélectionné si valide, sinon None.
        """

        # Tableau de choix pour les roles
        roles_list = Role.get_roles_list(self.session)
        table = Table()
        table.add_column("ID", style="cyan")
        table.add_column("Nom", style="cyan")
        table.add_row("0", "Annuler")
        for role in roles_list:
            table.add_row(str(role.Id), role.RoleName)

        self.view.display_table(table, "Liste des roles")

        while True:

            role_id = self.view.return_choice("Entrez l'identifiant du rôle de l'employé", False, f"{role_default}")

            try:
                selected_role = next((role for role in roles_list if role.Id == int(role_id)), None)
                if selected_role:
                    self.view.display_green_message(f"Rôle sélectionné : {selected_role.RoleName}")
                    return int(role_id)
                else:
                    return None
            except ValueError:
                self.view.display_red_message("Choix invalide !")
