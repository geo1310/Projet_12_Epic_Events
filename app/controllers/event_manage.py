from typing import List, Optional

from rich.console import Console
from rich.table import Table

from models.contract import Contract
from models.customer import Customer
from models.employee import Employee
from models.event import Event
from models.role import Role
from permissions.permissions import Permissions
from views.views import View

from .utils_manage import UtilsManage


class EventManage:
    """
    Gère les opérations liées aux évènements, telles que l'affichage, la création, la mise à jour et la suppression.
    """

    def __init__(self, session, employee, role):
        self.session = session
        self.view = View()
        self.console = Console()
        self.permissions = Permissions()
        self.employee = employee
        self.role = role
        self.user_connected_id = employee.Id
        self.utils = UtilsManage(self.employee)

    def get_permissions_events(self) -> List[Event]:
        """
        Récupère les événements autorisés en fonction du rôle de l'utilisateur connecté.

        Returns:
            List[Event]: Liste des événements autorisés.
        """

        if self.permissions.all_event(self.role):
            events = self.utils.filter(self.session, "All", None, Event)

        elif self.permissions.role_name(self.role) == "Commercial":
            events = (
                self.session.query(Event)
                .join(Contract, Event.ContractId == Contract.Id)
                .join(Customer, Contract.CustomerId == Customer.Id)
                .filter(Customer.CommercialId == self.user_connected_id)
                .all()
            )

        elif self.permissions.role_name(self.role) == "support":
            events = self.session.query(Event).filter(Event.EmployeeSupportRel == self.user_connected_id).all()

        else:
            events = []

        return events

    def get_permissions_contracts_signed(self) -> List[Contract]:
        """
        Récupère les contrats signés autorisés en fonction du rôle de l'utilisateur connecté.

        Returns:
            List[Contract]: Liste des contrats signés autorisés.
        """

        if self.permissions.all_contract(self.role):
            contracts_signed = self.utils.filter(self.session, "ContractSigned", True, Contract)

        elif self.permissions.role_name(self.role) == "Commercial":
            contracts_signed = (
                self.session.query(Contract)
                .join(Customer, Contract.CustomerId == Customer.Id)
                .filter(Customer.CommercialId == self.user_connected_id)
                .filter(Contract.ContractSigned == True)
                .all()
            )
        else:
            contracts_signed = []

        return contracts_signed

    def list(self) -> None:
        """
        Affiche une liste de tous les événements.

        Cette méthode récupère tous les événements en utilisant la méthode `filter` avec les paramètres appropriés,
        crée un tableau avec les événements récupérés en utilisant `table_event_create`, et affiche ce tableau via
        la vue.

        Returns:
            None
        """
        events = self.utils.filter(self.session, "All", None, Event)
        table = self.utils.table_create("event", events)
        self.view.display_table(table, "Liste des Evènements")

    def list_no_support(self) -> None:
        """
        Affiche une liste des événements sans support.

        Cette méthode récupère tous les événements qui n'ont pas de support en utilisant la méthode `filter` avec les
        paramètres appropriés, crée un tableau avec les événements récupérés en utilisant `table_event_create`, et
        affiche ce tableau via la vue.

        Returns:
            None
        """
        events = self.utils.filter(self.session, "EmployeeSupportId", None, Event)
        table = self.utils.table_create("event", events)
        self.view.display_table(table, "Liste des Evènements sans support")

    def list_yours_events(self) -> None:

        events = self.get_permissions_events()

        table = self.utils.table_create("event", events)
        self.view.display_table(table, "Liste de vos Evènements")

    def create(self) -> None:
        """
        Crée un nouvel événement et l'ajoute à la base de données.

        Cette méthode récupère les données nécessaires en appelant la méthode `_get_data`,
        puis demande à l'utilisateur d'entrer les informations requises pour créer un événement.
        La méthode valide les dates et le contrat avant de créer l'événement et de l'ajouter
        à la base de données.

        Attributs:
            self.event (Event): L'instance de l'événement créé.
            self.contracts (list): Liste des contrats accessibles par l'utilisateur connecté.
            self.contracts_signed (list): Liste des contrats signés accessibles par l'utilisateur connecté.

        Exceptions:
            IntegrityError: Levée en cas d'erreur d'intégrité de la base de données.
            ValueError: Levée en cas d'erreur de validation des données.
            Exception: Levée en cas d'autre erreur lors de la création de l'événement.
        """

        self.view.display_title_panel_color_fit("Création d'un évènement", "green")

        contracts_signed = self.get_permissions_contracts_signed()

        if not contracts_signed:
            self.view.display_red_message("Il n'y a aucuns de vos contrats signés pour affecter l'évènement !!!")
            return

        title = self.view.return_choice("Entrez le Titre de l'évènement ( vide pour annuler )", False)
        if not title:
            return

        notes = self.view.return_choice("Description ( facultatif )", False)
        location = self.view.return_choice("Lieu ( facultatif )", False)

        # validation des places
        attendees = self.validation_attendees("Attendees", "Nb de places")

        # validation des dates
        date_start = self.validation_date("date_start", "Date de début au format jj-mm-aaaa ( facultatif )")
        date_end = self.validation_date("date_end", "Date de fin au format jj-mm-aaaa ( facultatif )")

        contract_id = self.valid_contract(contracts_signed)
        if not contract_id:
            return

        # Instance du nouvel évènement
        event = Event(
            ContractId=contract_id,
            Title=title,
            Notes=notes,
            Location=location,
            Attendees=attendees,
            DateStart=date_start,
            DateEnd=date_end,
        )

        # validation du support pour l'évènement
        employee_support_id = None
        if self.permissions.can_access_support(self.role):

            # liste des employes du support
            role = self.session.query(Role).filter_by(RoleName="Support").one()
            employees_support = role.EmployeesRel
            # choix du support
            employee_support_id = self.valid_list(employees_support)

        if employee_support_id:
            event.EmployeeSupportId = employee_support_id

        self.utils.valid_oper(self.session, "event", "create", event)

    def update(self) -> None:
        """
        Modifie un évènement après validation de son identifiant et confirmation de l'utilisateur.

        Cette méthode permet à l'utilisateur de modifier les détails d'un évènement existant.
        Elle effectue les opérations suivantes :
        1. Récupère les évènements autorisés à modifier et les contrats signés.
        2. Vérifie s'il y a des évènements à modifier.
        3. Valide l'existence de l'évènement à modifier et demande confirmation à l'utilisateur.
        4. Affiche les détails de l'évènement à modifier.
        5. Demande à l'utilisateur de saisir les nouvelles informations de l'évènement.
        6. Valide et met à jour les informations de l'évènement dans la base de données.

        Exceptions:
            ValueError: Si l'identifiant de l'évènement n'est pas valide.
            IntegrityError: Si une contrainte d'intégrité de la base de données est violée.
            Exception: Pour toute autre erreur rencontrée lors de la modification de l'évènement.
        """

        events = self.get_permissions_events()
        contracts_signed = self.get_permissions_contracts_signed()

        if not events:
            self.view.display_red_message("Vous n'avez aucuns évènements à modifier !!!")
            return

        self.view.display_title_panel_color_fit("Modification d'un évènement", "yellow")

        # Validation de l'évènement à modifier par son Id
        event = self.utils.valid_id(self.session, Event, "évènement à modifier", events)
        if not event:
            return

        # affichage et confirmation de modification
        if not self.utils.confirm_table_recap("event", event, "Modification", "yellow"):
            return

        self.view.display_title_panel_color_fit("Modification d'un évènement", "yellow", True)

        event.Title = self.view.return_choice("Entrez le Titre de l'évènement", False, event.Title)
        event.Notes = self.view.return_choice("Description", False, event.Notes)
        event.Location = self.view.return_choice("Lieu", False, event.Location)

        # validation des places
        event.Attendees = self.validation_attendees("Attendees", "Nb de places", event.Attendees)

        # validation des dates
        event.DateStart = self.validation_date("date_start", "Date de début au format jj-mm-aaaa", event.DateStart)
        event.DateEnd = self.validation_date("date_end", "Date de fin au format jj-mm-aaaa", event.DateEnd)

        # validation du contrat
        if self.permissions.role_name(self.role) != "Support":
            event.ContractId = self.valid_contract(contracts_signed, event.ContractId)

        # validation du support pour l'évènement
        if self.permissions.can_access_support(self.role):

            role = self.session.query(Role).filter_by(RoleName="Support").one()
            employees_support = role.EmployeesRel
            event.EmployeeSupportId = self.valid_list(employees_support, event.EmployeeSupportId)

        self.utils.valid_oper(self.session, "event", "update", event)

    def delete(self) -> None:
        """
        Supprime un événement après validation de son identifiant et confirmation de l'utilisateur.

        Cette méthode effectue les opérations suivantes :
        1. Affiche le titre de la section de suppression d'événement.
        2. Demande à l'utilisateur de saisir l'identifiant de l'événement à supprimer.
        3. Valide l'existence de l'événement et vérifie que l'utilisateur est autorisé à le supprimer.
        4. Demande une confirmation de suppression.
        5. Supprime l'événement de la base de données et gère les éventuelles erreurs.

        Exceptions:
            ValueError: Si l'identifiant de l'événement n'est pas valide.
            IntegrityError: Si une contrainte d'intégrité de la base de données est violée.
            Exception: Pour toute autre erreur rencontrée lors de la suppression de l'événement.
        """

        events = self.get_permissions_events()

        self.view.display_title_panel_color_fit("Suppression d'un évènement", "red")

        if not events:
            self.view.display_red_message("Vous n'avez aucuns évènements à supprimer !!!")
            return

        # Validation de l'évènement à supprimer par son Id
        event = self.utils.valid_id(self.session, Event, "évènement à supprimer", events)
        if not event:
            return

        self.utils.valid_oper(self.session, "event", "delete", event)

    def valid_contract(self, contracts: List[Contract], default: Optional[int] = None) -> Optional[int]:
        """
        Valide et retourne l'identifiant d'un contrat sélectionné par l'utilisateur pour un évènement.

        Cette méthode affiche une liste des contrats signés accessibles par l'utilisateur, permet à l'utilisateur de choisir
        un contrat parmi cette liste et retourne l'identifiant du contrat sélectionné.

        Args:
            contracts (List[Contract]): La liste des contrats parmi lesquels l'utilisateur peut faire un choix.
            default (Optional[int], optional): L'identifiant par défaut du contrat sélectionné (par défaut None).

        Returns:
            Optional[int]: L'identifiant du contrat sélectionné par l'utilisateur, ou None si aucun contrat n'est sélectionné.
        """

        # Tableau de choix pour les contrats
        table = Table()
        table.add_column("ID", style="cyan")
        table.add_column("Titre", style="cyan")
        table.add_column("Contrat signé", style="cyan")
        table.add_row("0", "Aucun")

        for contract in contracts:
            table.add_row(str(contract.Id), contract.Title, "oui" if contract.ContractSigned else "non")

        self.view.display_table(table, "Liste des contrats signés")

        while True:

            contract_id = self.view.return_choice(
                "Entrez l'identifiant du contrat pour l'évènement", False, f"{default}"
            )

            try:
                selected_contract = next((contract for contract in contracts if contract.Id == int(contract_id)), None)
                if selected_contract:
                    self.view.display_green_message(f"Contrat sélectionné : {selected_contract.Title}")
                    return int(contract_id)
                else:
                    return None
            except Exception:
                self.view.display_red_message("Choix invalide !")

    def validation_date(self, key: str, message: str, default: Optional[str] = None) -> Optional[str]:
        """
        Valide une date en utilisant la fonction de validation de la classe Event.

        Cette méthode demande à l'utilisateur de saisir une date, vérifie si la date est valide
        et renvoie la date si elle est valide. Si la date n'est pas valide, elle affiche un message
        d'erreur et demande à l'utilisateur de réessayer.

        Args:
            key (str): Le champ de la date à valider (par exemple, "DateStart" ou "DateEnd").
            message (str): Le message à afficher lors de la demande de saisie de la date.
            default (str, optional): La valeur par défaut pour la date. Par défaut, None.

        Returns:
            str: La date validée sous forme de chaîne de caractères si elle est valide, sinon None.

        Raises:
            ValueError: Si la date n'est pas valide.
        """

        while True:
            date = self.view.return_choice(f"{message}", False, str(default.strftime("%d-%m-%Y")) if default else None)
            if not date:
                return None
            try:
                Event.check_dates(self, key, date)
            except Exception as e:
                self.view.display_red_message(f"Erreur de validation : {e}")

            else:
                return date

    def validation_attendees(self, key: str, message: str, default: any = None) -> Optional[int]:
        """
        Valide l'entrée pour le nombre de participants ('Attendees') d'un événement.

        Cette méthode demande à l'utilisateur d'entrer un nombre de participants jusqu'à ce qu'une entrée valide soit fournie.
        Elle effectue les vérifications suivantes :
        1. Vérifie que l'entrée est un entier valide.
        2. Vérifie que l'entier est non négatif.

        Args:
            key (str): Le nom de l'attribut en cours de validation.
            message (str): Le message affiché pour demander l'entrée de l'utilisateur.
            default (any): La valeur par défaut pour l'entrée.

        Returns:
            Optional[int]: Le nombre validé de participants, ou None si l'utilisateur annule l'entrée.

        Exceptions:
            ValueError: Si la valeur entrée n'est pas un entier valide ou si elle est négative.
        """
        while True:
            attendees = self.view.return_choice(f"{message}", False, str(default) if default else None)
            if not attendees:
                return 0
            try:
                Event.check_attendees(self, key, attendees)
            except Exception as e:
                self.view.display_red_message(f"Erreur de validation : {e}")
            else:
                return int(attendees)

    def valid_list(self, employees_support: List[Employee], default: Optional[int] = None) -> Optional[int]:
        """
        Valide et retourne l'identifiant d'un employé de support sélectionné par l'utilisateur pour un évènement.

        Cette méthode affiche une liste des employés de support disponibles, permet à l'utilisateur de choisir
        un employé parmi cette liste et retourne l'identifiant de l'employé sélectionné.

        Args:
            employees_support (List[Employee]): La liste des employés de support disponibles.
            default (int, optional): L'identifiant par défaut de l'employé sélectionné (par défaut None).

        Returns:
            int: L'identifiant de l'employé de support sélectionné par l'utilisateur, ou None si aucun employé n'est sélectionné.
        """

        # Tableau de choix pour les employés de support
        table = Table()
        table.add_column("ID", style="cyan")
        table.add_column("Nom", style="cyan")
        table.add_column("Prénom", style="cyan")
        table.add_row("0", "Aucun")

        for employee in employees_support:
            table.add_row(str(employee.Id), employee.FirstName, employee.LastName)

        self.view.display_table(table, "Liste des employés de support")

        while True:
            employee_id = self.view.return_choice(
                "Entrez l'identifiant de l'employé de support pour l'évènement", False, f"{default}"
            )

            try:
                selected_employee = next(
                    (employee for employee in employees_support if employee.Id == int(employee_id)), None
                )
                if selected_employee:
                    self.view.display_green_message(
                        f"Employé sélectionné : {selected_employee.FirstName} {selected_employee.LastName}"
                    )
                    return int(employee_id)
                elif employee_id == "0":
                    return None
                else:
                    self.view.display_red_message("Choix invalide !")
            except ValueError:
                self.view.display_red_message("Choix invalide !")
            except Exception:
                self.view.display_red_message("Choix invalide !")
