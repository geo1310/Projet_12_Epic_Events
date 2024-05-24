from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
import bcrypt
from sqlalchemy.exc import IntegrityError
from email.utils import parseaddr
import re

from ..models.database import Session
from ..models.employee import Employee
from ..models.role import Role
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
        """
        Affiche la liste des employés dans un tableau.

        Args:
            arg: Argument optionnel pour passer des paramètres supplémentaires.
        """

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
        self.view.display_table(table, "Liste des employés.")
        self.view.prompt_wait_enter()

    def create(self, arg):
        """
        Crée un nouvel employé après avoir collecté et validé les informations de l'utilisateur.

        Args:
            arg: Argument optionnel pour passer des paramètres supplémentaires.
        """
        self.view.display_title_panel_color_fit("Création d'un employé", "green")

        # Collecte les informations de l'utilisateur

        first_name = self.view.return_choice("Entrez le prénom de l'employé ( facultatif ): ", False)
        last_name = self.view.return_choice("Entrez le nom de famille de l'employé ( facultatif ): ", False)
        email = self.validation_email()
        if not email:
            return
        
        self.view.display_green_message("Email validé !")

        password_hash = self.validation_password()
        if not password_hash:
            return
        
        self.view.display_green_message("Mot de passe validé !")
        
        # validation du role
        # Tableau de choix pour les roles
        roles_list = Role.get_roles_list(self.session)
        table = Table()
        table.add_column("ID", style="cyan")
        table.add_column("Nom", style="magenta")
        table.add_row("0", "Annuler")
        for role in roles_list:
            table.add_row(str(role.Id), role.RoleName)

        self.view.display_table(table, "Liste des roles")

        while True:
            role_id = self.view.return_choice("Entrez l'identifiant du rôle de l'employé: ", False)
            try:
                selected_role = next((role for role in roles_list if role.Id == int(role_id)), None)
                if selected_role:
                    self.view.display_green_message(f"Rôle sélectionné : {selected_role.RoleName}")
                    break
                else:
                    return
            except ValueError as e:
                self.view.display_red_message("Choix invalide !")
            

        # Instance du nouvel objet Employee
        self.employee = Employee(
            FirstName=first_name, LastName=last_name, Email=email, PasswordHash=password_hash, RoleId=int(role_id)
        )

        # Ajouter à la session et commit
        try:
            self.session.add(self.employee)
            self.session.flush()
            # Affichage et confirmation
            if not self.confirm_table_recap("Création", "green"):
                self.session.expunge(self.employee)
                self.session.rollback()
                return
            self.session.commit()
            self.view.display_green_message("\nEmployé créé avec succès !")
        except IntegrityError as e:
            self.session.rollback()
            error_detail = e.args[0].split("DETAIL:")[1] if e.args else "Erreur inconnue"
            self.view.display_red_message(f"Erreur : {error_detail}")
        except ValueError as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur de validation : {e}")
        except Exception as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur lors de la création de l'employé : {e}")

        self.view.prompt_wait_enter()

    def update(self, arg):
        # TODO
        pass

    def delete(self, arg):

        self.view.display_title_panel_color_fit("Suppression d'un employé", "red")

        while True:
            employee_id = self.view.return_choice("Entrez l'identifiant de l'employé à supprimer ( vide pour annuler ): ", False)
            
            if not employee_id:
                return
            
            try:
                self.employee = self.session.query(Employee).filter_by(Id=int(employee_id)).one()
                break
            except Exception:
                self.view.display_red_message("Identifiant non valide !")


        if not self.confirm_table_recap("Suppression", "red"):
            return

        try:
            self.session.delete(self.employee)
            self.session.commit()
            self.view.display_green_message("Employé supprimé avec succès !")
        except IntegrityError as e:
            self.session.rollback()
            error_detail = e.args[0].split("DETAIL:")[1] if e.args else "Erreur inconnue"
            self.view.display_red_message(f"Erreur : {error_detail}")
        except Exception as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur lors de la suppression de l'employé : {e}")

        self.view.prompt_wait_enter()

    def format_date(self, date):
        if date:
            return date.strftime("%d/%m/%Y")
        return None

    def validation_email(self):
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
            email = self.view.return_choice("Entrez l'adresse email de l'employé ( vide pour annuler ): ", False)
            if not email:
                return None
            try:
                Employee.validate_email(self, "email", email)
            except ValueError as e:
                self.view.display_red_message(f"Erreur de validation : {e}")
            else:
                return email

    def validation_password(self):
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
            password = self.view.return_choice("Entrez le mot de passe de l'employé ( vide pour annuler ): ", True)
            if not password:
                return None
            confirm_password = self.view.return_choice(
                "Confirmez le mot de passe de l'employé ( vide pour annuler ): ", True
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

    def confirm_table_recap(self,oper:str, color:str="white"):
        """
        Affiche un tableau récapitulatif des informations de l'employé et demande une confirmation.

        Cette méthode crée et affiche un tableau récapitulatif contenant les informations de l'employé.
        Ensuite, elle demande à l'utilisateur de confirmer l'opération en saisissant 'oui' ou 'non'. 
        Si l'utilisateur confirme, la méthode retourne True. 

        Args:
        oper (str): L'opération à confirmer (par exemple, 'Création', 'Mise à jour', 'Suppression').
        color (str): Couleur du texte

        Returns:
            bool: True si l'utilisateur confirme l'opération, False sinon.

        """

        self.view.display_title_panel_color_fit(f"{oper} d'un employé", f"{color}",True)

        # Tableau récapitulatif
        summary_table = Table()
        summary_table.add_column("Champ", style="cyan")
        summary_table.add_column("Valeur", style="magenta")
        summary_table.add_row("Prénom", self.employee.FirstName)
        summary_table.add_row("Nom", self.employee.LastName)
        summary_table.add_row("Email", self.employee.Email)
        summary_table.add_row("Rôle", self.employee.RoleRel.RoleName)

        self.view.display_table(summary_table, "Résumé de l'employé")

        # Demander une confirmation avant validation
        confirm = self.view.return_choice(f"Confirmation {oper} ? (oui/non): ", False)
        if confirm.lower() != 'oui':
            self.view.display_red_message("Opération annulée.")
            self.view.prompt_wait_enter()
            return False
        return True
