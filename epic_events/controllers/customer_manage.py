from datetime import datetime
from rich.console import Console
from rich.table import Table
from sqlalchemy.exc import IntegrityError

from ..permissions.permissions import Permissions
from ..models.customer import Customer
from ..models.employee import Employee
from ..models.role import Role
from ..models.database import Session
from ..views.views import View


class CustomerManage:
    """
    Gère les opérations liées aux clients, telles que l'affichage, la création, la mise à jour et la suppression.
    """

    def __init__(self, user_connected_id):
        self.session = Session()
        self.view = View()
        self.console = Console()
        self.permissions = Permissions()
        self.user_connected_id = user_connected_id
        self.employee = self.session.query(Employee).filter_by(Id=user_connected_id).one()
        self.role = self.session.query(Role).filter_by(Id=self.employee.RoleId).one()


    def list(self):

        if self.permissions.can_access_all_customer(self.role):
            self.customers = self.session.query(Customer).all()
        else:
            self.customers = self.employee.CustomersRel

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

        for customer in self.customers:

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

    def create(self):
        """
        Crée un nouveau client associé au commercial connecté.

        Cette méthode permet de créer un nouveau client dans la base de données. Elle effectue les étapes suivantes :
        Demande à l'utilisateur de saisir les informations du client.
        Valide l'adresse email du client.
        Ajoute le client à la session et tente de le valider en base de données.
        Affiche un récapitulatif des informations du client et demande une confirmation avant de finaliser la création.
        Gère les erreurs potentielles, y compris les violations d'intégrité et les exceptions générales.

        Returns:
            None
        """
        
        self.view.display_title_panel_color_fit("Création d'un client", "green")

        first_name = self.view.return_choice("Entrez le prénom du client ( facultatif )", False)
        last_name = self.view.return_choice("Entrez le nom de famille du client ( facultatif )", False)

        # Validation de l'email
        email = self.validation_email()
        if not email:
            return
        self.view.display_green_message("Email validé !")

        phone_number = self.view.return_choice("Entrez le numéro de téléphone du client ( facultatif )", False)
        company_name = self.view.return_choice("Entrez l'entreprise du client ( facultatif )", False)

        commercial_id = self.user_connected_id

        # Instance du nouvel objet Employee
        self.customer = Customer(
            FirstName=first_name, LastName=last_name, Email=email, PhoneNumber=phone_number, Company=company_name, CommercialId=commercial_id
        )
        
        # Ajouter à la session et commit
        try:
            self.session.add(self.customer)
            self.session.flush()

            # Affichage et confirmation de la création
            if not self.confirm_table_recap("Création", "green"):
                self.session.expunge(self.customer)
                self.session.rollback()
                return
            self.session.commit()
            self.view.display_green_message("\nClient créé avec succès !")
        except IntegrityError as e:
            self.session.rollback()
            error_detail = e.args[0].split("DETAIL:")[1] if e.args else "Erreur inconnue"
            self.view.display_red_message(f"Erreur : {error_detail}")
        except ValueError as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur de validation : {e}")
        except Exception as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur lors de la création du client : {e}")
        
        self.view.prompt_wait_enter()

    def update(self):
        """
        Met à jour les informations d'un client existant dans la base de données.

        Cette méthode permet de modifier les informations d'un client spécifique. Elle effectue les étapes suivantes :
        Demande à l'utilisateur de saisir les informations du client.
        Met à jour le champ DateLastUpdate avec le timestamp actuel.
        Valide les modifications et les enregistre dans la base de données.
        Gère les erreurs potentielles, y compris les violations d'intégrité et les exceptions générales.

        Returns:
            None
        """
        self.view.display_title_panel_color_fit("Modification d'un client", "yellow")

        self.customers = self.employee.CustomersRel

        # Validation du client à modifier par son Id
        while True:
            customer_id = self.view.return_choice(
                "Entrez l'identifiant du client à modifier ( vide pour annuler )", False
            )

            if not customer_id:
                return

            try:
                self.customer = self.session.query(Customer).filter_by(Id=int(customer_id)).one()
                
                # vérifie que le client est dans la liste des clients de l'employé
                if self.customer in self.customers or self.permissions.can_access_all_customer(self.role):
                    break
                self.view.display_red_message("Vous n'etes pas autorisé à modifier ce client !")

            except Exception:
                self.view.display_red_message("Identifiant non valide !")

        # affichage et confirmation de modification
        if not self.confirm_table_recap("Modification", "yellow"):
            return
        
        self.view.display_title_panel_color_fit("Modification d'un employé", "yellow", True)
        self.customer.FirstName = self.view.return_choice("Prénom", False, f"{self.customer.FirstName}")
        self.customer.LastName = self.view.return_choice("Nom", False, f"{self.customer.LastName}")
        self.customer.Email = self.view.return_choice("Email", False, f"{self.customer.Email}")
        self.customer.PhoneNumber = self.view.return_choice("Numéro de Téléphone", False, f"{self.customer.PhoneNumber}")
        self.customer.Company = self.view.return_choice("Entreprise", False, f"{self.customer.Company}")
        self.customer.DateLastUpdate = datetime.now()

        # Ajouter à la session et commit
        try:
            self.session.commit()

            # Affichage et confirmation de la modification
            if not self.confirm_table_recap("Modification", "yellow"):
                self.session.expunge(self.customer)
                self.session.rollback()
                return

            self.view.display_green_message("\nClient modifié avec succès !")
        except IntegrityError as e:
            self.session.rollback()
            error_detail = e.args[0].split("DETAIL:")[1] if e.args else "Erreur inconnue"
            self.view.display_red_message(f"Erreur : {error_detail}")
        except ValueError as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur de validation : {e}")
        except Exception as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur lors de la modification : {e}")

        self.view.prompt_wait_enter()

    def delete(self):
        """
        Supprime un client associé au commercial connecté.

        Cette méthode permet de supprimer un client de la base de données. Elle effectue les étapes suivantes :
        Charge la liste des clients associés au commercial connecté.
        Demande à l'utilisateur de saisir l'identifiant du client à supprimer.
        Vérifie que le client appartient bien au commercial connecté.
        Demande une confirmation avant la suppression.
        Supprime le client de la base de données et confirme la réussite de l'opération.
        Gère les erreurs potentielles, y compris les violations d'intégrité et les exceptions générales.

        Returns:
            None
        """

        self.view.display_title_panel_color_fit("Suppression d'un client", "red")

        self.customers = self.employee.CustomersRel

        # Validation du client à supprimer par son Id
        while True:
            customer_id = self.view.return_choice(
                "Entrez l'identifiant de l'employé à supprimer ( vide pour annuler )", False
            )

            if not customer_id:
                return
            try:
                self.customer = self.session.query(Customer).filter_by(Id=int(customer_id)).one()
                
                # vérifie que le client est dans la liste des clients de l'employé
                if self.customer in self.customers or self.permissions.can_access_all_customer(self.role):
                    break
                self.view.display_red_message("Vous n'etes pas autorisé à supprimer ce client !")
            except Exception:
                self.view.display_red_message("Identifiant non valide !")

        # confirmation de suppression
        if not self.confirm_table_recap("Suppression", "red"):
            return
        
        try:
            self.session.delete(self.customer)
            self.session.commit()
            self.view.display_green_message("Client supprimé avec succès !")
        except IntegrityError as e:
            self.session.rollback()
            error_detail = e.args[0].split("DETAIL:")[1] if e.args else "Erreur inconnue"
            self.view.display_red_message(f"Erreur : {error_detail}")
        except Exception as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur lors de la suppression : {e}")
        
        self.view.prompt_wait_enter()

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
                Customer.validate_email(self, "email", email)
            except ValueError as e:
                self.view.display_red_message(f"Erreur de validation : {e}")
            else:
                return email
            
    def confirm_table_recap(self, oper: str, color: str = "white"):
        """
        Affiche un tableau récapitulatif des informations du client et demande une confirmation.

        Cette méthode crée et affiche un tableau récapitulatif contenant les informations du client.
        Ensuite, elle demande à l'utilisateur de confirmer l'opération en saisissant 'oui' ou 'non'.
        Si l'utilisateur confirme, la méthode retourne True.

        Args:
        oper (str): L'opération à confirmer (par exemple, 'Création', 'Mise à jour', 'Suppression').
        color (str): Couleur du texte

        Returns:
            bool: True si l'utilisateur confirme l'opération, False sinon.

        """

        self.view.display_title_panel_color_fit(f"{oper} d'un client", f"{color}", True)

        # Tableau récapitulatif
        summary_table = Table()
        summary_table.add_column("Champ", style="cyan")
        summary_table.add_column("Valeur", style="magenta")
        summary_table.add_row("Prénom", self.customer.FirstName)
        summary_table.add_row("Nom", self.customer.LastName)
        summary_table.add_row("Email", self.customer.Email)
        summary_table.add_row("Tél", self.customer.PhoneNumber)
        summary_table.add_row("Companie", self.customer.Company)

        self.view.display_table(summary_table, "Résumé du client")

        # Demander une confirmation avant validation
        confirm = self.view.return_choice(f"Confirmation {oper} ? (oui/non)", False)
        if confirm:
            confirm = confirm.lower()
        if confirm != "oui":
            self.view.display_red_message("Opération annulée.")
            self.view.prompt_wait_enter()
            return False
        return True
