from typing import List, Type
from rich.table import Table
from sqlalchemy.exc import IntegrityError
from app.views.views import View
from app.utils.sentry_logger import SentryLogger 


from app.models.role import Role
from app.models.employee import Employee
from app.models.customer import Customer
from app.models.contract import Contract
from app.models.event import Event


class UtilsManage:
    """
    Classe utilitaire pour gérer diverses opérations sur les modèles de l'application.

    Cette classe contient des méthodes pour afficher des récapitulatifs, créer des tableaux, formater des dates,
    convertir des chaînes en booléens, filtrer des instances de modèles, et valider des identifiants et des opérations.

    Attributs:
        view (View): Instance de la classe View pour gérer l'affichage.
        sentry (SentryLogger): Instance de la classe SentryLogger pour gérer la journalisation des événements.
        employee (Employee): L'employé qui effectue les opérations.

    """

    def __init__(self, employee):
        self.view = View()
        self.sentry = SentryLogger()
        self.employee = employee

    def confirm_table_recap(self, model_name: str, model_instance, oper: str, color: str = "white") -> bool:
        """
        Affiche un récapitulatif d'une opération sur un modèle et demande une confirmation de l'utilisateur.

        Cette méthode affiche un tableau récapitulatif de l'opération effectuée sur une instance de modèle et demande à
        l'utilisateur de confirmer l'opération avant de procéder.

        Args:
            model_name (str): Le nom du modèle concerné par l'opération.
            model_instance_ : L'instance du modèle sur laquelle l'opération est effectuée.
            oper (str): Le type d'opération à effectuer (ex : "Création", "Modification", "Suppression").
            color (str, optional): La couleur à utiliser pour afficher le titre du panneau. Par défaut "white".

        Returns:
            bool: True si l'utilisateur confirme l'opération, False sinon.
        """

        self.view.display_title_panel_color_fit(f"{model_name} - {oper}", f"{color}", True)

        summary_table = self.table_create(model_name, [model_instance])

        self.view.display_table(summary_table, f"Résumé - {model_name}")

        # Demander une confirmation avant validation
        confirm = self.view.return_choice(f"Confirmation {oper} ? (oui/non)", False)
        if confirm:
            confirm = confirm.lower()
        if confirm != "oui":
            self.view.display_red_message("Opération annulée.")
            return False
        return True
    
    def table_create(self, arg1: str, list: List) -> Table:
        """
        Crée et retourne un tableau en fonction du type spécifié.

        Cette méthode prend en entrée un type d'objet (event, contract, customer, employee, role) et une liste 
        d'instances de ce type, puis retourne un tableau formaté pour afficher ces instances.

        Args:
            arg1 (str): Le type d'objet pour lequel créer le tableau. Les valeurs possibles sont "event", "contract", 
                        "customer", "employee" et "role".
            list (List): Une liste d'instances de l'objet spécifié.

        Returns:
            Table: Un tableau formaté pour afficher les instances de l'objet spécifié.

        Raises:
            ValueError: Si `arg1` ne correspond à aucun type d'objet connu.
        """

        if arg1 == "event":
            return self.table_event(list)
        
        elif arg1 == "contract":
            return self.table_contract(list)
        
        elif arg1 == "customer":
            return self.table_customer(list)
        
        elif arg1 == "employee":
            return self.table_employee(list)
        
        elif arg1 == "role":
            return self.table_role(list)
        
        else:
            raise ValueError(f"Unknown type: {arg1}")
            
        
    def table_event(self, events: List[Event])-> Table:
        """
        Crée et retourne un tableau pour afficher les événements.

        Args:
            events (List[Event]): Une liste d'instances d'événements à afficher dans le tableau.

        Returns:
            Table: Un tableau formaté pour afficher les événements avec leurs détails.
        """
    
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
    
    def table_contract(self, contracts: List[Contract]):
        """
        Crée et retourne un tableau pour afficher les contrats.

        Args:
            contracts (List[Contract]): Une liste d'instances de contrats à afficher dans le tableau.

        Returns:
            Table: Un tableau formaté pour afficher les contrats avec leurs détails.
        """

        table = Table(show_header=True, header_style="bold green")
        table.add_column("ID", style="dim", width=5)
        table.add_column("Titre")
        table.add_column("Nom du Client")
        table.add_column("Email du Client")
        table.add_column("Nom du Commercial")
        table.add_column("Email du Commercial")
        table.add_column("Montant")
        table.add_column("Montant restant")
        table.add_column("Contrat signé")
        table.add_column("Date de création")

        for contract in contracts:
            # Récupérer les infos du commercial associé au client
            if contract.CustomerRel:
                customer_last_name = contract.CustomerRel.LastName
                customer_email = contract.CustomerRel.Email
                commercial_last_name = (
                    contract.CustomerRel.CommercialRel.LastName if contract.CustomerRel.CommercialRel else None
                )
                commercial_email = contract.CustomerRel.CommercialRel.Email if contract.CustomerRel.CommercialRel else None
            else:
                commercial_last_name = ""
                commercial_email =  ""
                customer_last_name = ""
                customer_email = ""

            table.add_row(
                str(contract.Id),
                contract.Title,
                customer_last_name,
                customer_email,
                commercial_last_name,
                commercial_email,
                str(contract.Amount),
                str(contract.AmountOutstanding),
                str(contract.ContractSigned),
                self.format_date(contract.DateCreated),
            )

        return table
    
    def table_customer(self, customers: List[Customer])-> Table:
        """
        Crée et retourne un tableau pour afficher les clients.

        Args:
            customers (List[Customer]): Une liste d'instances de clients à afficher dans le tableau.

        Returns:
            Table: Un tableau formaté pour afficher les clients avec leurs détails.
        """

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
    
    def table_employee(self, employees: List[Employee])-> Table:
        """
        Crée et retourne un tableau pour afficher les détails des employés.

        Args:
            employees (List[Employee]): Une liste d'instances d'employés à afficher dans le tableau.

        Returns:
            Table: Un tableau formaté pour afficher les employés avec leurs détails.
        """

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
    
    def table_role(self, roles: List[Role])-> Table:
        """
        Crée et retourne un tableau pour afficher les détails des rôles.

        Args:
            roles (List[Role]): Une liste d'instances de rôles à afficher dans le tableau.

        Returns:
            Table: Un tableau formaté pour afficher les rôles avec leurs détails.
        """

        table = Table(show_header=True, header_style="bold green")
        table.add_column("ID", style="dim", width=3)
        table.add_column("Nom")
        table.add_column("R. employee")
        table.add_column("U. employee")
        table.add_column("CRUD. employee")
        table.add_column("R. role")
        table.add_column("U. role")
        table.add_column("CRUD. role")
        table.add_column("U. customer")
        table.add_column("CRUD customer")
        table.add_column("ALL customer")
        table.add_column("U. contract")
        table.add_column("CRUD contract")
        table.add_column("ALL contract")
        table.add_column("U event")
        table.add_column("CRUD event")
        table.add_column("ALL event")
        table.add_column("Support event")
        table.add_column("Date de création")

        for role in roles:
            
            table.add_row(
                str(role.Id),
                role.RoleName,
                str(role.Can_r_Employee),
                str(role.Can_ru_Employee),
                str(role.Can_crud_Employee),
                str(role.Can_r_Role),
                str(role.Can_ru_Role),
                str(role.Can_crud_Role),
                str(role.Can_ru_Customer),
                str(role.Can_crud_Customer),
                str(role.Can_access_all_Customer),
                str(role.Can_ru_Contract),
                str(role.Can_crud_Contract),
                str(role.Can_access_all_Contract),
                str(role.Can_ru_Event),
                str(role.Can_crud_Event),
                str(role.Can_access_all_Event),
                str(role.Can_access_support_Event),
                self.format_date(role.DateCreated),
            )

        return table
    

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
    

    def str_to_bool(self, str_value):
        """
        Convertit une chaîne de caractères en une valeur booléenne.

        Args:
            str_value (str): La chaîne de caractères à convertir.

        Returns:
            bool: Retourne True si la chaîne de caractères représente une valeur vraie, sinon False.
        """

        if str_value.lower() in ("true", "1", "oui"):
            return True
        return False
    

    def filter(self, session, attribute: str, value: any, model: Type) -> List:
        """
        Filtre les instances d'un modèle en fonction d'un attribut et d'une valeur spécifiques.

        Args:
            session (Session): La session SQLAlchemy utilisée pour interagir avec la base de données.
            attribute (str): Le nom de l'attribut du modèle sur lequel effectuer le filtre. 
                            Si "All", aucun filtre spécifique n'est appliqué.
            value (any): La valeur de l'attribut à filtrer. Si `None`, les instances où l'attribut est `Null` 
                        seront récupérées.
            model (Type): La classe du modèle SQLAlchemy à interroger.

        Returns:
            List: Une liste des instances du modèle qui correspondent aux critères de filtrage spécifiés.
        """
        query = session.query(model)

        if attribute != "All":
            if value is None:
                query = query.filter(getattr(model, attribute) == None)
            else:
                query = query.filter(getattr(model, attribute) == value)

        return query.all()
    

    def valid_id(self, session, model, message: str,  auhtorized_list: List= None):
        """
        Valide l'identifiant d'un élément en vérifiant qu'il existe dans la base de données et qu'il est autorisé.

        Args:
            session (Session): La session SQLAlchemy à utiliser pour interagir avec la base de données.
            model (Type): Le modèle de base de données SQLAlchemy à interroger.
            message (str): Le message à afficher pour demander l'identifiant.
            authorized_list (List): La liste des éléments autorisés pour cette opération.

        Returns:
            object or None: L'élément correspondant à l'identifiant s'il est valide et autorisé, sinon None.

        Exceptions:
            Affiche un message d'erreur en cas d'identifiant invalide ou si l'opération n'est pas autorisée.
        """

        while True:
            element_id = self.view.return_choice(
                f"Entrez l'Id: {message}  ( vide pour annuler )", False
            )

            if not element_id:
                return None

            try:
                element = session.query(model).filter_by(Id=int(element_id)).one()

                # vérifie que le contrat est dans la liste autorisée.
                if not auhtorized_list or element in auhtorized_list:
                    return element
                self.view.display_red_message("Opération non autorisée")

            except Exception as e:
                self.view.display_red_message(f"Identifiant non valide ! {e}")


    def valid_oper(self, session, model_name, oper: str, model_instance):
        """
        Valide l'identifiant d'un élément en vérifiant qu'il existe dans la base de données et qu'il est autorisé.

        Args:
            session (Session): La session SQLAlchemy à utiliser pour interagir avec la base de données.
            model (Type): Le modèle de base de données SQLAlchemy à interroger.
            message (str): Le message à afficher pour demander l'identifiant.
            authorized_list (List, optional): La liste des éléments autorisés pour cette opération. 
                Si spécifiée, l'élément doit appartenir à cette liste pour être considéré comme autorisé.
                Par défaut, None.

        Returns:
            object or None: L'élément correspondant à l'identifiant s'il est valide et autorisé, sinon None.

        Exceptions:
            Affiche un message d'erreur en cas d'identifiant invalide ou si l'opération n'est pas autorisée.
        """
        
        try:
            if oper == "create":
                session.add(model_instance)
            elif oper == "update":
                session.merge(model_instance)
            elif oper == "delete":
                session.delete(model_instance)
            else:
                raise ValueError("Invalid operation. Supported operations: 'create', 'update', 'delete'.")

            session.flush()

            # Affichage et confirmation de la création
            if not self.confirm_table_recap(model_name, model_instance, oper, "green"):
                session.expunge(model_instance)
                session.rollback()
                return
            session.commit()
            self.view.display_green_message(f"\n{model_name} - {oper} -> Success")

            # évènement sentry
            self.sentry.sentry_event(
                self.employee.Email,
                f"{model_name} - {oper}",
                "info",
                f"{model_name}-{oper}",
            )

        except IntegrityError as e:
            session.rollback()
            self.view.display_red_message(f"Erreur d'intégrité : {e.orig}")
        except ValueError as e:
            session.rollback()
            self.view.display_red_message(f"Erreur de validation : {e}")
        except Exception as e:
            session.rollback()
            self.view.display_red_message(f"Erreur: {e}")


