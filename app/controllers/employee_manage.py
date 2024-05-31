from typing import List, Type
import sentry_sdk
from email.utils import parseaddr

from rich.console import Console
from rich.table import Table
from sqlalchemy.exc import IntegrityError

from models.database import SessionLocal
from models.employee import Employee
from models.role import Role
from views.views import View

from .utils_manage import sentry_event



class EmployeeManage:
    """
    Gère les opérations liées aux employés, telles que l'affichage, la création, la mise à jour et la suppression.
    """

    def __init__(self, user_connected_id):
        self.session = SessionLocal()
        self.view = View()
        self.console = Console()
        self.employee = self.session.query(Employee).filter_by(Id=user_connected_id).one()
        self.role = self.session.query(Role).filter_by(Id=self.employee.RoleId).one()
        

    def list(self):
        employees = self.filter("All", None, Employee)
        table = self.table_employee_create(employees)
        self.view.display_table(table, "Liste des Employés")

    @sentry_sdk.trace
    def create(self):
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

        # Ajouter à la session et commit
        try:
            self.session.add(employee)
            self.session.flush()

            # Affichage et confirmation de la création
            if not self.confirm_table_recap(employee, "Création", "green"):
                self.session.expunge(employee)
                self.session.rollback()
                return
            self.session.commit()
            self.view.display_green_message("\nEmployé créé avec succès !")
            
            # évènement sentry
            sentry_event(self.employee.Email, f"Employé créé: Prénom: {employee.FirstName} - Nom: {employee.LastName} - Email: {employee.Email}", "Employee_create")
            
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

    def update(self):
        """
        Mets à jour les informations d'un employé existant.

        Cette méthode permet de modifier les informations d'un employé en demandant à l'utilisateur
        de saisir un identifiant d'employé, puis de valider les nouvelles informations fournies. Les
        modifications sont affichées pour confirmation avant d'être enregistrées dans la base de données.

        Args:
            arg: Argument optionnel pour passer des paramètres supplémentaires.
        """
        self.view.display_title_panel_color_fit("Modification d'un employé", "yellow")

        # Validation de l'employé à modifier par son Id
        while True:
            employee_id = self.view.return_choice(
                "Entrez l'identifiant de l'employé à supprimer ( vide pour annuler )", False
            )

            if not employee_id:
                return

            try:
                employee = self.session.query(Employee).filter_by(Id=int(employee_id)).one()
                break
            except Exception:
                self.view.display_red_message("Identifiant non valide !")

        # Affichage et confirmation de la modification
        if not self.confirm_table_recap(employee, "Modification", "yellow"):
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

        # Ajouter à la session et commit
        try:
            self.session.commit()

            # Affichage et confirmation de la modification
            if not self.confirm_table_recap(employee, "Modification", "yellow"):
                self.session.expunge(employee)
                self.session.rollback()
                return

            self.view.display_green_message("\nEmployé modifié avec succès !")
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

    @sentry_sdk.trace
    def delete(self):
        """
        Supprime un employé existant.

        Cette méthode permet de supprimer un employé en demandant à l'utilisateur
        de saisir un identifiant d'employé, puis de valider la suppression.
        La suppression est affichée pour confirmation avant d'être exécutée.

        Args:
            arg: Argument optionnel pour passer des paramètres supplémentaires.
        """

        self.view.display_title_panel_color_fit("Suppression d'un employé", "red")

        # Validation de l'employé à supprimer par son Id
        while True:
            employee_id = self.view.return_choice(
                "Entrez l'identifiant de l'employé à supprimer ( vide pour annuler )", False
            )

            if not employee_id:
                return

            try:
                employee = self.session.query(Employee).filter_by(Id=int(employee_id)).one()
                break
            except Exception:
                self.view.display_red_message("Identifiant non valide !")

        if not self.confirm_table_recap(employee, "Suppression", "red"):
            return

        try:
            self.session.delete(employee)
            self.session.commit()
            self.view.display_green_message("Employé supprimé avec succès !")

            # évènement sentry
            sentry_event(self.employee.Email, f"Employé supprimé : Prénom: {employee.FirstName} - Nom: {employee.LastName} - Email: {employee.Email}", "Employee_create")

        except IntegrityError as e:
            self.session.rollback()
            error_detail = e.args[0].split("DETAIL:")[1] if e.args else "Erreur inconnue"
            self.view.display_red_message(f"Erreur : {error_detail}")
        except Exception as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur lors de la suppression de l'employé : {e}")

    def format_date(self, date: str):
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
            email = self.view.return_choice("Entrez l'adresse email de l'employé ( vide pour annuler )", False)
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

    def confirm_table_recap(self, employee: Employee, oper: str, color: str = "white"):

        self.view.display_title_panel_color_fit(f"{oper} d'un employé", f"{color}", True)

        summary_table = self.table_employee_create([employee])

        self.view.display_table(summary_table, "Résumé de l'employé")

        # Demander une confirmation avant validation
        confirm = self.view.return_choice(f"Confirmation {oper} ? (oui/non)", False)
        if confirm:
            confirm = confirm.lower()
        if confirm != "oui":
            self.view.display_red_message("Opération annulée.")
            return False
        return True

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
        table.add_column("Nom", style="magenta")
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

    def table_employee_create(self, employees: List[Employee]) -> Table:
        """
        Crée un tableau pour afficher les employés.

        Cette méthode prend une liste d'employés en entrée et génère un tableau contenant les détails de chaque employé
        pour affichage.

        Args:
            employees (List[Employee]): Une liste d'objets Employee à afficher dans le tableau.

        Returns:
            Table: Un objet Table de la bibliothèque Rich contenant les informations des employés.
        """

        # Création du tableau pour afficher les employés
        table = Table(show_header=True, header_style="bold green")
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

        return table

    def filter(self, attribute: str, value: any, model: Type) -> List:
        """
        Filtre les instances du modèle en fonction d'un attribut et d'une valeur spécifiés.

        Args:
            attribute (str): L'attribut du modèle par lequel filtrer. Si "All", aucun filtrage n'est appliqué.
            value (Any): La valeur de l'attribut pour filtrer les instances du modèle. Peut être n'importe quelle valeur,
                         y compris None pour filtrer les valeurs NULL.
            model (Type): La classe du modèle SQLAlchemy à filtrer (par exemple, Event, Employee).

        Returns:
            List: Une liste des instances du modèle qui correspondent aux critères de filtrage.
        """
        query = self.session.query(model)

        if attribute != "All":
            if value is None:
                query = query.filter(getattr(model, attribute) == None)
            else:
                query = query.filter(getattr(model, attribute) == value)

        return query.all()
