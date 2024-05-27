from rich.console import Console
from rich.table import Table
from sqlalchemy.exc import IntegrityError
from ..permissions.permissions import Permissions
from ..models.contract import Contract
from ..models.customer import Customer
from ..models.employee import Employee
from ..models.role import Role

from ..models.database import Session
from ..models.event import Event
from ..views.views import View


class EventManage:
    """
    Gère les opérations liées aux évènements, telles que l'affichage, la création, la mise à jour et la suppression.
    """

    def __init__(self, user_connected_id):
        self.session = Session()
        self.view = View()
        self.console = Console()
        self.permissions = Permissions()
        self.user_connected_id = user_connected_id
        self.employee = self.session.query(Employee).filter_by(Id=user_connected_id).one()
        self.role = self.session.query(Role).filter_by(Id=self.employee.RoleId).one()

    def _get_data(self):
        """
        Récupère et initialise les données nécessaires.
        incluant les contrats et les clients selon les autorisations de l'utilisateur connecté.

        Attributs:
            self.events (list): Liste des évènements accessibles par l'utilisateur connecté.
            self.contracts (list): Liste des contrats accessibles par l'utilisateur connecté.
            self.contracts_signed (list): Liste des contrats signés accessibles par l'utilisateur connecté

        """

        # liste des évènements selon autorisation
        if self.permissions.can_access_all_event(self.role):
            self.events = self.session.query(Event).all()
        elif self.permissions.can_read_event(self.role) and self.permissions.can_create_delete_event(self.role):
            self.events = (
            self.session.query(Event)
            .join(Contract, Event.ContractId == Contract.Id)
            .join(Customer, Contract.CustomerId == Customer.Id)
            .filter(Customer.CommercialId == self.user_connected_id)
            .all()
            )
        elif self.permissions.can_read_event(self.role) and not self.permissions.can_create_delete_event(self.role):
            self.events = (
            self.session.query(Event)
            .filter(Event.EmployeeSupportId == self.user_connected_id)
            .all()
        )
            

        # liste des contrats selon autorisation
        if self.permissions.can_access_all_customer(self.role):
            self.contracts = self.session.query(Contract).all()
        else:
            self.contracts = (
                self.session.query(Contract)
                .join(Customer, Contract.CustomerId == Customer.Id)
                .filter(Customer.CommercialId == self.user_connected_id)
                .all()
            )
            # Filtrer les contrats signés
            self.contracts_signed = (
                self.session.query(Contract)
                .filter(Contract.ContractSigned == True)  # Filtrer les contrats signés
                .filter(Contract.CustomerId.in_([customer.Id for customer in self.contracts]))  # Filtrer les contrats appartenant aux clients du commercial connecté
                .all()
            )

    def list(self):
        """
        Affiche une liste des événements accessibles par l'utilisateur connecté.

        Cette méthode récupère les données nécessaires en appelant la méthode `_get_data` 
        puis crée et affiche un tableau contenant les informations des événements. 

        Attributs:
            self.events (list): Liste des événements accessibles par l'utilisateur connecté.

        """
       
        self._get_data()

        # création du tableau
        table = Table(show_header=True, header_style="bold green")
        # Ajouter des colonnes
        table.add_column("ID", style="dim", width=5)
        table.add_column("Titre")
        table.add_column("Notes")
        table.add_column("location")
        table.add_column("Places")
        table.add_column("Contrat")
        table.add_column("Employé Support")
        table.add_column("Date de début")
        table.add_column("Date de fin")
        table.add_column("Date de création")

        for event in self.events:

            employee_support = ""
            if event.EmployeeSupportRel:
                employee_support = event.EmployeeSupportRel.FirstName

            table.add_row(
                str(event.Id),
                event.Title,
                event.Notes,
                event.Location,
                str(event.Attendees),
                event.ContractRel.Title,
                employee_support,
                self.format_date(event.DateStart),
                self.format_date(event.DateEnd),
                self.format_date(event.DateCreated),
            )

        # Affiche le tableau
        self.view.display_table(table, "\nListe des Evènements")
        self.view.prompt_wait_enter()

    def create(self):
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
        self._get_data()

        self.view.display_title_panel_color_fit("Création d'un évènement", "green")

        title = self.view.return_choice("Entrez le Titre de l'évènement ( vide pour annuler )", False)
        if not title:
            return
        
        notes = self.view.return_choice("Description ( facultatif )", False)
        location = self.view.return_choice("Lieu ( facultatif )", False)
        attendees = self.view.return_choice("Nb de places ( facultatif )", False)
        
        # validation des dates
        date_start = self.validation_date("date_start", "Date de début au format jj-mm-aaaa ( facultatif )")
        date_end = self.validation_date("date_end", "Date de fin au format jj-mm-aaaa ( facultatif )")

        # validation du contrat
        contract_id = self.valid_contract()
        if not contract_id:
            return
        
        # Instance du nouvel évènement
        self.event = Event(
            ContractId = contract_id,
            Title = title,
            Notes = notes,
            Location = location,
            Attendees = attendees,
            DateStart = date_start,
            DateEnd = date_end,
        )

        # Ajouter à la session et commit
        try:
            self.session.add(self.event)
            self.session.flush()

            # Affichage et confirmation de la création
            if not self.confirm_table_recap("Création", "green"):
                self.session.expunge(self.event)
                self.session.rollback()
                return
            self.session.commit()
            self.view.display_green_message("\nEvènement créé avec succès !")
        except IntegrityError as e:
            self.session.rollback()
            error_detail = e.args[0].split("DETAIL:")[1] if e.args else "Erreur inconnue"
            self.view.display_red_message(f"Erreur : {error_detail}")
        except ValueError as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur de validation : {e}")
        except Exception as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur lors de la création: {e}")


        self.view.prompt_wait_enter()

    def update(self):
        # TODO
        pass

    def delete(self):
        # TODO
        pass

    def format_date(self, date: str):
        """
        Formate une date en chaîne de caractères au format "JJ/MM/AAAA HH:MN".
        """
        if date:
            return date.strftime("%d/%m/%Y %H:%M")
        return None
    
    def valid_contract(self, default=None):
        """
        Valide et retourne l'identifiant d'un contrat sélectionné par l'utilisateur pour un évènement.

        Cette méthode affiche une liste des contrats signés accessibles par l'utilisateur, permet à l'utilisateur de choisir
        un contrat parmi cette liste et retourne l'identifiant du contrat sélectionné.

        Args:
            default (int): L'identifiant par défaut du contrat sélectionné (par défaut None).

        Returns:
            int: L'identifiant du contrat sélectionné par l'utilisateur, ou None si aucun contrat n'est sélectionné.
        """

        # Tableau de choix pour les contrats
        table = Table()
        table.add_column("ID", style="cyan")
        table.add_column("Titre", style="magenta")
        table.add_column("Contrat signé", style="magenta")
        table.add_row("0", "Annuler")

        for contract in self.contracts_signed:
            table.add_row(str(contract.Id), contract.Title, "oui" if contract.ContractSigned else "non")

        self.view.display_table(table, "Liste des contrats signés")

        while True:

            contract_id = self.view.return_choice(
                "Entrez l'identifiant du contrat pour l'évènement", False, f"{default}"
            )

            try:
                selected_contract = next(
                    (contract for contract in self.contracts_signed if contract.Id == int(contract_id)), None
                )
                if selected_contract:
                    self.view.display_green_message(f"Contrat sélectionné : {selected_contract.Title}")
                    return int(contract_id)
                else:
                    return None
            except ValueError:
                self.view.display_red_message("Choix invalide !")
            except Exception:
                self.view.display_red_message("Choix invalide !")

    def validation_date(self, key, message):
        """
        Valide une date en utilisant la fonction de validation de la classe Event.

        Cette méthode demande à l'utilisateur de saisir une date, vérifie si la date est valide
        et renvoie la date si elle est valide. Si la date n'est pas valide, elle affiche un message
        d'erreur et demande à l'utilisateur de réessayer.

        Args:
            key (str): Le champ de la date à valider (par exemple, "DateStart" ou "DateEnd").
            message (str): Le message à afficher lors de la demande de saisie de la date.

        Returns:
            date (str): La date validée sous forme de chaîne de caractères si elle est valide, sinon None.
        """

        while True:
            date = self.view.return_choice(f"{message}", False)
            if not date:
                return None
            try:
                Event.check_dates(self, key, date)
            except ValueError as e:
                self.view.display_red_message(f"Erreur de validation : {e}")
            else:
                return date
            
    def confirm_table_recap(self, oper: str, color: str = "white"):
        """
        Affiche un récapitulatif des détails de l'événement et demande une confirmation.

        Cette méthode affiche un tableau récapitulatif des détails de l'événement en cours,
        puis demande à l'utilisateur de confirmer l'opération (par exemple, création, modification,
        suppression). Si l'utilisateur confirme, la méthode retourne True. Sinon, elle affiche
        un message d'annulation et retourne False.

        Args:
            oper (str): Le type d'opération à confirmer (par exemple, "Création", "Modification", "Suppression").
            color (str): La couleur à utiliser pour le titre du récapitulatif (par défaut "white").

        Returns:
            bool: True si l'utilisateur confirme l'opération, False sinon.
        """

        self.view.display_title_panel_color_fit(f"{oper} d'un évènement", f"{color}", True)

        # Tableau récapitulatif
        summary_table = Table()
        summary_table.add_column("Champ", style="cyan")
        summary_table.add_column("Valeur", style="magenta")
        summary_table.add_row("Contrat", self.event.ContractRel.Title)
        summary_table.add_row("Titre", self.event.Title)
        summary_table.add_row("Description", self.event.Notes)
        summary_table.add_row("Lieu", self.event.Location)
        summary_table.add_row("Nombre de places", str(self.event.Attendees))
        summary_table.add_row("Date de début", str(self.event.DateStart))
        summary_table.add_row("Date de fin", str(self.event.DateEnd))

        self.view.display_table(summary_table, "Résumé de l'évènement")

        # Demander une confirmation avant validation
        confirm = self.view.return_choice(f"Confirmation {oper} ? (oui/non)", False)
        if confirm:
            confirm = confirm.lower()
        if confirm != "oui":
            self.view.display_red_message("Opération annulée.")
            self.view.prompt_wait_enter()
            return False
        return True
