from typing import List, Optional, Type
from datetime import datetime
from rich.console import Console
from rich.table import Table
from sqlalchemy.exc import IntegrityError

from ..models.customer import Customer
from ..models.database import Session
from ..models.employee import Employee
from ..models.role import Role
from ..permissions.permissions import Permissions
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

        customers = self.filter("All", None, Customer)
        table = self.table_customer_create(customers)
        self.view.display_table(table, "Liste des Clients")

    def list_yours_customers(self):
        if self.permissions.role_name(self.role) == "Commercial":
            customers = self.filter("CommercialId", self.user_connected_id, Customer)
        else:
            customers = []
            
        table = self.table_customer_create(customers)
        self.view.display_table(table, "Liste des Clients")

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
            FirstName=first_name,
            LastName=last_name,
            Email=email,
            PhoneNumber=phone_number,
            Company=company_name,
            CommercialId=commercial_id,
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
                customer = self.session.query(Customer).filter_by(Id=int(customer_id)).one()

                # vérifie que le client est dans la liste des clients de l'employé
                if customer in self.customers:
                    break
                self.view.display_red_message("Vous n'etes pas autorisé à modifier ce client !")

            except Exception:
                self.view.display_red_message("Identifiant non valide !")

        # affichage et confirmation de modification
        if not self.confirm_table_recap(customer, "Modification", "yellow"):
            return

        self.view.display_title_panel_color_fit("Modification d'un client", "yellow", True)
        customer.FirstName = self.view.return_choice("Prénom", False, f"{customer.FirstName}")
        customer.LastName = self.view.return_choice("Nom", False, f"{customer.LastName}")
        customer.Email = self.view.return_choice("Email", False, f"{customer.Email}")
        customer.PhoneNumber = self.view.return_choice(
            "Numéro de Téléphone", False, f"{customer.PhoneNumber}"
        )
        customer.Company = self.view.return_choice("Entreprise", False, f"{customer.Company}")
        customer.DateLastUpdate = datetime.now()

        # Ajouter à la session et commit
        try:
            self.session.commit()

            # Affichage et confirmation de la modification
            if not self.confirm_table_recap(customer, "Modification", "yellow"):
                self.session.expunge(customer)
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
                customer = self.session.query(Customer).filter_by(Id=int(customer_id)).one()

                # vérifie que le client est dans la liste des clients de l'employé
                if customer in self.customers:
                    break
                self.view.display_red_message("Vous n'etes pas autorisé à supprimer ce client !")
            except Exception:
                self.view.display_red_message("Identifiant non valide !")

        # confirmation de suppression
        if not self.confirm_table_recap(customer, "Suppression", "red"):
            return

        try:
            self.session.delete(customer)
            self.session.commit()
            self.view.display_green_message("Client supprimé avec succès !")
        except IntegrityError as e:
            self.session.rollback()
            error_detail = e.args[0].split("DETAIL:")[1] if e.args else "Erreur inconnue"
            self.view.display_red_message(f"Erreur : {error_detail}")
        except Exception as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur lors de la suppression : {e}")


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
            email = self.view.return_choice("Entrez l'adresse email ( vide pour annuler )", False)
            if not email:
                return None
            try:
                Customer.validate_email(self, "email", email)
            except ValueError as e:
                self.view.display_red_message(f"Erreur de validation : {e}")
            else:
                return email

    def confirm_table_recap(self, customer: Customer, oper: str, color: str = "white"):
        
        self.view.display_title_panel_color_fit(f"{oper} d'un client", f"{color}", True)
        summary_table = self.table_customer_create([customer])
        self.view.display_table(summary_table, "Résumé du client")

        # Demander une confirmation avant validation
        confirm = self.view.return_choice(f"Confirmation {oper} ? (oui/non)", False)
        if confirm:
            confirm = confirm.lower()
        if confirm != "oui":
            self.view.display_red_message("Opération annulée.")
            return False
        return True
    
    def table_customer_create(self, customers: List[Customer]) -> Table:
        

        table = Table(show_header=True, header_style="bold green")
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
