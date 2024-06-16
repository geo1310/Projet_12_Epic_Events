from typing import List

from rich.console import Console
from rich.table import Table

from models.contract import Contract
from models.customer import Customer
from permissions.permissions import Permissions
from utils.sentry_logger import SentryLogger
from views.views import View

from .utils_manage import UtilsManage


class ContractManage:
    """
    Gère les opérations liées aux contrats, telles que l'affichage, la création, la mise à jour et la suppression.
    """

    def __init__(self, session, employee, role):
        self.session = session
        self.view = View()
        self.console = Console()
        self.permissions = Permissions()
        self.employee = employee
        self.role = role
        self.user_connected_id = employee.Id
        self.sentry = SentryLogger()
        self.utils = UtilsManage(self.employee)

    def get_permissions_contracts(self):
        # liste des contrats autorisés
        if self.permissions.all_contract(self.role):
            contracts = self.utils.filter(self.session, "All", None, Contract)

        elif self.permissions.role_name(self.role) == "Commercial":
            contracts = (
                self.session.query(Contract)
                .join(Customer, Contract.CustomerId == Customer.Id)
                .filter(Customer.CommercialId == self.user_connected_id)
                .all()
            )

        else:
            contracts = []

        return contracts

    def get_permissions_customers(self):

        # liste des clients autorisés
        if self.permissions.all_customer(self.role):
            customers = self.utils.filter(self.session, "All", None, Customer)

        elif self.permissions.role_name(self.role) == "Commercial":
            customers = (
                self.session.query(Customer)
                .join(Contract, Customer.CommercialId == Contract.CustomerId)
                .filter(Customer.CommercialId == self.user_connected_id)
                .all()
            )

        else:
            return None

        return customers

    def list(self) -> None:
        """
        Affiche une liste de tous les contrats.

        Cette méthode récupère tous les contrats en utilisant la méthode `filter` avec les paramètres appropriés,
        crée un tableau avec les événements récupérés en utilisant `table_event_create`, et affiche ce tableau via
        la vue.

        Returns:
            None
        """
        contracts = self.utils.filter(self.session, "All", None, Contract)
        table = self.utils.table_create("contract", contracts)
        self.view.display_table(table, "Liste des Contrats")

    def list_yours_contracts(self):

        contracts = self.get_permissions_contracts()

        table = self.utils.table_create("contract", contracts)
        self.view.display_table(table, "Liste de vos Contrats")

    def list_yours_contracts_not_signed(self):

        contracts_not_signed = (
            self.session.query(Contract)
            .join(Customer, Contract.CustomerId == Customer.Id)
            .filter(Customer.CommercialId == self.user_connected_id)
            .filter(Contract.ContractSigned == False)
            .all()
        )

        table = self.utils.table_create("contract", contracts_not_signed)
        self.view.display_table(table, "Liste de vos Contrats non signés")

    def list_yours_contracts_not_payed(self):
        contracts_not_payed = (
            self.session.query(Contract)
            .join(Customer, Contract.CustomerId == Customer.Id)
            .filter(Customer.CommercialId == self.user_connected_id)
            .filter(Contract.AmountOutstanding != 0)
            .all()
        )

        table = self.utils.table_create("contract", contracts_not_payed)
        self.view.display_table(table, "Liste de vos Contrats non payés")

    def create(self):
        """
        Crée un nouveau contrat.

        Cette méthode permet de créer un nouveau contrat en saisissant les détails nécessaires
        via des invites à l'utilisateur. Elle gère également la validation des données
        saisies et assure que le contrat est correctement lié à un client existant.

        Workflow:
            1. Récupère les données nécessaires (contrats et clients) via la méthode `_get_data`.
            2. Affiche le titre de la section de création.
            3. Demande à l'utilisateur de saisir le titre du contrat.
            4. Valide et sélectionne le client associé au contrat.
            5. Demande à l'utilisateur de saisir les montants et vérifie leur validité.
            6. Demande à l'utilisateur de saisir l'état de signature du contrat.
            7. Crée une instance du contrat avec les données saisies.
            8. Ajoute le contrat à la session et tente de le valider en base de données.
            9. Affiche et confirme la création du contrat.
            10. Gère les exceptions potentielles et affiche les messages d'erreur appropriés.

        Exceptions:
            IntegrityError: Si une contrainte d'intégrité de la base de données est violée.
            ValueError: Si la validation des montants échoue.
            Exception: Pour toutes autres erreurs inattendues.

        Returns:
            None
        """

        customers = self.get_permissions_customers()
        if not customers:
            self.view.display_red_message("Aucuns clients autorisés pour le contrat !")
            return

        self.view.display_title_panel_color_fit("Création d'un contrat", "green")

        title = self.view.return_choice("Entrez le Titre du contrat ( vide pour annuler )", False)
        if not title:
            return

        # validation du client lié au contrat
        customer_id = self.valid_customer(customers)
        if not customer_id:
            return

        # validation des détails du contrat
        amount = self.validation_amount("Montant du contrat", "amount")
        amount_outstanding = self.validation_amount(
            "Montant restant du", "amount_outstanding", f"{amount if amount else None}"
        )
        contract_signed = self.utils.str_to_bool(
            self.view.return_choice("Contrat signé", False, "non", ("oui", "non"))
        )

        # Instance du nouveau contrat
        contract = Contract(
            CustomerId=customer_id,
            Title=title,
            Amount=amount,
            AmountOutstanding=amount_outstanding,
            ContractSigned=contract_signed,
        )

        self.utils.valid_oper(self.session, "contract", "create", contract)

    def update(self):
        """
        Met à jour les détails d'un contrat existant.

        Cette méthode permet de modifier les informations d'un contrat sélectionné par son identifiant.
        L'utilisateur est guidé à travers un processus de saisie pour mettre à jour les champs du contrat.
        La méthode assure également que seules les personnes autorisées peuvent modifier un contrat donné.

        Workflow:
            1. Affiche le titre de la section de modification.
            2. Demande l'identifiant du contrat à modifier.
            3. Vérifie que l'utilisateur est autorisé à modifier le contrat.
            4. Affiche et confirme les modifications.
            5. Met à jour les champs du contrat avec les nouvelles valeurs.
            6. Valide le client lié au contrat.
            7. Enregistre les modifications dans la base de données.

        Exceptions:
            ValueError: Si la validation des montants échoue.
            IntegrityError: Si une contrainte d'intégrité de la base de données est violée.
            Exception: Pour toutes autres erreurs inattendues.

        Returns:
            None
        """

        contracts = self.get_permissions_contracts()

        customers = self.get_permissions_customers()
        if not customers:
            self.view.display_red_message("Aucuns clients autorisés pour le contrat !")
            return

        self.view.display_title_panel_color_fit("Modification d'un contrat", "yellow")

        if not contracts:
            self.view.display_red_message("Vous n'avez aucuns contrats à modifier !!!")
            return

        # Validation du contrat à modifier par son Id
        contract = self.utils.valid_id(self.session, Contract, "contrat à modifier", contracts)
        if not contract:
            return

        # affichage et confirmation de modification
        if not self.utils.confirm_table_recap("contract", contract, "Modification", "yellow"):
            return

        self.view.display_title_panel_color_fit("Modification d'un contrat", "yellow", True)

        contract.Title = self.view.return_choice("Titre", False, f"{contract.Title}")
        contract.Amount = self.validation_amount("Montant du contrat", "amount", contract.Amount)
        contract.AmountOutstanding = self.validation_amount(
            "Montant restant du", "amount_outstanding", contract.AmountOutstanding
        )

        contract.ContractSigned = self.utils.str_to_bool(
            self.view.return_choice(
                "Contrat signé", False, f"{'oui' if contract.ContractSigned else 'non'}", ("oui", "non")
            )
        )

        if self.permissions.role_name(self.role) == "Gestion":

            # validation du client lié au contrat
            contract.CustomerId = self.valid_customer(customers, contract.CustomerId)
            if not contract.CustomerId:
                return

        self.utils.valid_oper(self.session, "contract", "update", contract)

    def delete(self):
        """
        Supprime un contrat existant.

        Cette méthode permet de supprimer un contrat de la base de données.
        L'utilisateur est invité à entrer l'identifiant du contrat à supprimer,
        et la méthode vérifie si l'utilisateur est autorisé à supprimer ce contrat.
        Si l'identifiant est valide et que l'utilisateur est autorisé, le contrat est supprimé
        après une confirmation.

        Raises:
            ValueError: Si l'identifiant du contrat n'est pas valide.
            Exception: Pour toute autre erreur lors de la suppression du contrat.
        """

        contracts = self.get_permissions_contracts()

        self.view.display_title_panel_color_fit("Suppression d'un contrat", "red")

        # Validation du contrat à modifier par son Id
        contract = self.utils.valid_id(self.session, Contract, "contrat à supprimer", contracts)
        if not contract:
            return

        self.utils.valid_oper(self.session, "contract", "delete", contract)

    def validation_amount(self, message: str, key: str, default: str = "0"):
        """
        Valide et convertit un montant saisi par l'utilisateur.

        Cette méthode affiche un message à l'utilisateur, lui demande de saisir un montant,
        et valide ensuite que le montant est bien un nombre flottant. Si la validation échoue,
        un message d'erreur est affiché et l'utilisateur est invité à saisir à nouveau le montant.

        Args:
            message (str): Le message à afficher pour demander le montant à l'utilisateur.
            key (str): Le nom du champ montant (utilisé dans la validation).
            default (str): La valeur par défaut à utiliser si l'utilisateur ne saisit rien (par défaut "0").

        Returns:
            float: Le montant validé saisi par l'utilisateur.
        """

        while True:
            amount = self.view.return_choice(f"{message}", False, f"{default}")

            try:
                Contract.validate_amount(self, f"{key}", amount)
            except ValueError as e:
                self.view.display_red_message(f"Erreur de validation : {e}")
            else:
                return amount

    def valid_customer(self, customers: List[Customer], default=None):
        """
        Affiche une liste de clients et permet à l'utilisateur de sélectionner un client pour un contrat.

        Args:
            customers (List[Customer]): La liste des clients disponibles pour sélection.
            default (optional): Valeur par défaut à afficher pour la sélection. Par défaut, None.

        Returns:
            int or None: L'identifiant du client sélectionné si un client est sélectionné, sinon None.

        Exceptions:
            Affiche un message d'erreur en cas de choix invalide ou si une exception se produit.
        """

        # Tableau de choix pour les clients
        table = Table()
        table.add_column("ID", style="cyan")
        table.add_column("Prénom", style="cyan")
        table.add_column("Nom", style="cyan")
        table.add_column("Email", style="cyan")
        table.add_row("0", "Annuler")

        for customer in customers:
            table.add_row(str(customer.Id), customer.FirstName, customer.LastName, customer.Email)

        self.view.display_table(table, "Liste des clients")

        while True:

            customer_id = self.view.return_choice(
                "Entrez l'identifiant du client pour le contrat", False, f"{default}"
            )

            try:
                selected_customer = next((customer for customer in customers if customer.Id == int(customer_id)), None)
                if selected_customer:
                    self.view.display_green_message(f"Client sélectionné : {selected_customer.Email}")
                    return int(customer_id)
                else:
                    return None
            except ValueError:
                self.view.display_red_message("Choix invalide !")
            except Exception:
                self.view.display_red_message("Choix invalide !")
