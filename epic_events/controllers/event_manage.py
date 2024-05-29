from typing import List, Optional, Type
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


    def get_permissions_events(self):

        if self.permissions.all_event(self.role):
            events = self.filter("All", None, Event)

        elif self.permissions.role_name(self.role) == "Commercial":
            events = (
                self.session.query(Event)
                .join(Contract, Event.ContractId == Contract.Id)
                .join(Customer, Contract.CustomerId == Customer.Id)
                .filter(Customer.CommercialId == self.user_connected_id)
                .all()
            )

        elif self.permissions.role_name(self.role) == "support":
            events = (
                self.session.query(Event)
                .filter(Event.EmployeeSupportRel == self.user_connected_id)
                .all()
            )
        
        else:
            events = []

        return events

    def list(self) -> None:
        """
        Affiche une liste de tous les événements.

        Cette méthode récupère tous les événements en utilisant la méthode `filter` avec les paramètres appropriés,
        crée un tableau avec les événements récupérés en utilisant `table_event_create`, et affiche ce tableau via
        la vue.

        Returns:
            None
        """
        events = self.filter("All", None, Event)
        table = self.table_event_create(events)
        self.view.display_table(table, "Liste des Evènements")
        self.view.prompt_wait_enter()

    def list_no_support(self) -> None:
        """
        Affiche une liste des événements sans support.

        Cette méthode récupère tous les événements qui n'ont pas de support en utilisant la méthode `filter` avec les
        paramètres appropriés, crée un tableau avec les événements récupérés en utilisant `table_event_create`, et
        affiche ce tableau via la vue.

        Returns:
            None
        """
        events = self.filter("EmployeeSupportId", None, Event)
        table = self.table_event_create(events)
        self.view.display_table(table, "Liste des Evènements sans support")
        self.view.prompt_wait_enter()

    def list_yours_events(self)-> None:

        events = self.get_permissions_events()

        table = self.table_event_create(events)
        self.view.display_table(table, "Liste de vos Evènements")
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

        self.view.display_title_panel_color_fit("Création d'un évènement", "green")

        # liste des contrats signés
        if self.permissions.all_contract(self.role):
            contracts = self.filter("ContractSigned", True, Contract)
        elif self.permissions.role_name(self.role) == "Commercial":
            contracts = (
                self.session.query(Contract)
                .join(Customer, Contract.CustomerId == Customer.Id)
                .filter(Customer.CommercialId == self.user_connected_id)
                .filter(Contract.ContractSigned == True)
                .all()
            )
        else:
            contracts = []

        if not contracts:    
            self.view.display_red_message("Il n'y a aucuns de vos contrats signés pour affecter l'évènement !!!")
            self.view.prompt_wait_enter()
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


        contract_id = self.valid_contract(contracts)
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

        # Ajouter à la session et commit
        try:
            self.session.add(event)
            self.session.flush()

            # Affichage et confirmation de la création
            if not self.confirm_table_recap(event, "Création", "green"):
                self.session.expunge(event)
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

        events = self.get_permissions_events()

        if not events:    
            self.view.display_red_message("Vous n'avez aucuns évènements à modifier !!!")
            self.view.prompt_wait_enter()
            return

        self.view.display_title_panel_color_fit("Modification d'un évènement", "yellow")

        # Validation de l'évènement à modifier par son Id
        while True:
            event_id = self.view.return_choice(
                "Entrez l'identifiant de l'évènement à modifier ( vide pour annuler )", False
            )

            if not event_id:
                return

            try:
                event = self.session.query(Event).filter_by(Id=int(event_id)).one()

                # vérifie que l'évènement est dans la liste autorisée.
                if event in events:
                    break
                self.view.display_red_message("Vous n'etes pas autorisé à modifier cet évènement !")

            except Exception:
                self.view.display_red_message("Identifiant non valide !")

        # affichage et confirmation de modification
        if not self.confirm_table_recap(event, "Modification", "yellow"):
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
            contracts = self.filter("ContractSigned", True, Contract)
            event.ContractId = self.valid_contract(contracts, event.ContractId)

        # validation du support pour l'évènement
        if self.permissions.can_access_support(self.role):

            role = self.session.query(Role).filter_by(RoleName="Support").one()
            employees_support = role.EmployeesRel
            event.EmployeeSupportId = self.valid_list(employees_support, event.EmployeeSupportId)

        # Ajouter à la session et commit
        try:
            self.session.commit()

            # Affichage et confirmation de la modification
            if not self.confirm_table_recap(event, "Modification", "yellow"):
                self.session.expunge(event)
                self.session.rollback()
                return

            self.view.display_green_message("\nEvènement modifié avec succès !")
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
        Supprime un événement après validation de son identifiant et confirmation de l'utilisateur.

        Cette méthode effectue les opérations suivantes :
        1. Affiche le titre de la section de suppression d'événement.
        2. Demande à l'utilisateur de saisir l'identifiant de l'événement à supprimer.
        3. Valide l'existence de l'événement et vérifie que l'utilisateur est autorisé à le supprimer.
        4. Demande une confirmation de suppression.
        5. Supprime l'événement de la base de données et gère les éventuelles erreurs.

        Raises:
            ValueError: Si l'identifiant de l'événement n'est pas valide.
            IntegrityError: Si une contrainte d'intégrité de la base de données est violée.
            Exception: Pour toute autre erreur rencontrée lors de la suppression de l'événement.
        """

        events = self.get_permissions_events()

        self.view.display_title_panel_color_fit("Suppression d'un évènement", "red")

        if not events:    
            self.view.display_red_message("Vous n'avez aucuns évènements à supprimer !!!")
            self.view.prompt_wait_enter()
            return

        # Validation de l'évènement à supprimer par son Id
        while True:
            event_id = self.view.return_choice(
                "Entrez l'identifiant de l'évènement à supprimer ( vide pour annuler )", False
            )

            if not event_id:
                return
            try:
                event = self.session.query(Event).filter_by(Id=int(event_id)).one()

                # vérifie que le contrat est dans la liste autorisée
                if event in events:
                    break
                self.view.display_red_message("Vous n'etes pas autorisé à supprimer cet évènement !")
            except Exception:
                self.view.display_red_message("Identifiant non valide !")

        # confirmation de suppression
        if not self.confirm_table_recap(event, "Suppression", "red"):
            return

        try:
            self.session.delete(event)
            self.session.commit()
            self.view.display_red_message("Evènement supprimé avec succès !")
        except IntegrityError as e:
            self.session.rollback()
            error_detail = e.args[0].split("DETAIL:")[1] if e.args else "Erreur inconnue"
            self.view.display_red_message(f"Erreur : {error_detail}")
        except Exception as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur lors de la suppression : {e}")

        self.view.prompt_wait_enter()

    def format_date(self, date: str) -> Optional[str]:
        """
        Formate une date en chaîne de caractères au format "JJ/MM/AAAA HH:MN".

        Args:
            date (str): La date à formater au format YYYY-MM-DD HH:MM.

        Returns:
            str: La date formatée au format "JJ/MM/AAAA HH:MN", ou None si la date fournie est vide.
        """
        if date:
            return date.strftime("%d/%m/%Y %H:%M")
        return None

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
        table.add_column("Titre", style="magenta")
        table.add_column("Contrat signé", style="magenta")
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
            except ValueError:
                self.view.display_red_message("Choix invalide !")
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
            except ValueError as e:
                self.view.display_red_message(f"Erreur de validation : {e}")
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

        Raises:
            ValueError: Si la valeur entrée n'est pas un entier valide ou si elle est négative.
        """
        while True:
            attendees = self.view.return_choice(f"{message}", False, str(default) if default else None)
            if not attendees:
                return 0
            try:
                Event.check_attendees(self, key, attendees)
            except ValueError as e:
                self.view.display_red_message(f"Erreur de validation : {e}")
            except Exception as e:
                self.view.display_red_message(f"Erreur de validation : {e}")
            else:
                return int(attendees)

    def confirm_table_recap(self, event: Event, oper: str, color: str = "white") -> bool:
        """
        Affiche un récapitulatif des détails de l'événement et demande une confirmation.

        Cette méthode affiche un tableau récapitulatif des détails de l'événement passé en paramètre,
        puis demande à l'utilisateur de confirmer l'opération spécifiée (par exemple, création, modification,
        suppression). Si l'utilisateur confirme, la méthode retourne True. Sinon, elle affiche un message
        d'annulation et retourne False.

        Args:
            event (Event): L'instance de l'événement à afficher dans le récapitulatif.
            oper (str): Le type d'opération à confirmer (par exemple, "Création", "Modification", "Suppression").
            color (str): La couleur à utiliser pour le titre du récapitulatif (par défaut "white").

        Returns:
            bool: True si l'utilisateur confirme l'opération, False sinon.
        """

        self.view.display_title_panel_color_fit(f"{oper} d'un évènement", f"{color}", True)

        summary_table = self.table_event_create([event])

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

    def table_event_create(self, events: List[Event]) -> Table:
        """
        Crée un tableau pour afficher les événements.

        Cette méthode prend une liste d'événements en entrée et génère un tableau contenant les détails de chaque événement
        pour affichage.

        Args:
            events (List[Event]): Une liste d'objets Event à afficher dans le tableau.

        Returns:
            Table: Un objet Table de la bibliothèque Rich contenant les informations des événements.
        """

        # Création du tableau pour afficher les événements
        table = Table(show_header=True, header_style="bold green")
        table.add_column("ID", style="dim", width=5)
        table.add_column("Titre")
        table.add_column("Notes")
        table.add_column("Location")
        table.add_column("Places")
        table.add_column("Contrat")
        table.add_column("Employé Support")
        table.add_column("Date de début")
        table.add_column("Date de fin")
        table.add_column("Date de création")

        for event in events:

            table.add_row(
                str(event.Id),
                event.Title,
                event.Notes,
                event.Location,
                str(event.Attendees),
                event.ContractRel.Title if event.ContractId else None,
                event.EmployeeSupportRel.FirstName if event.EmployeeSupportId else None,
                self.format_date(event.DateStart),
                self.format_date(event.DateEnd),
                self.format_date(event.DateCreated),
            )

        return table
    
    def table_contract_create(self, contracts: List[Contract]) -> Table:
        """
        Crée un tableau pour afficher les contrats.

        Cette méthode prend une liste de contrats en entrée et génère un tableau contenant les détails de chaque contrat
        pour affichage.

        Args:
            contracts (List[Contract]): Une liste d'objets Contract à afficher dans le tableau.

        Returns:
            Table: Un objet Table de la bibliothèque Rich contenant les informations des contrats.
        """

        # Création du tableau pour afficher les contrats
        table = Table(show_header=True, header_style="bold green")
        table.add_column("ID", style="dim", width=5)
        table.add_column("Titre")
        table.add_column("Nom du Client")
        table.add_column("Email du Client")
        table.add_column("Commercial")
        table.add_column("Montant")
        table.add_column("Montant restant")
        table.add_column("Contrat signé")
        table.add_column("Date de création")

        for contract in contracts:
            # Récupérer le nom du commercial associé au client
            commercial_name = contract.CustomerRel.CommercialRel.FirstName if contract.CustomerRel.CommercialRel else None

            table.add_row(
                str(contract.Id),
                contract.Title,
                contract.CustomerRel.FirstName,
                contract.CustomerRel.Email,
                commercial_name,
                str(contract.Amount),
                str(contract.AmountOutstanding),
                str(contract.ContractSigned),
                self.format_date(contract.DateCreated),
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
        table.add_column("Nom", style="magenta")
        table.add_column("Prénom", style="magenta")
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
