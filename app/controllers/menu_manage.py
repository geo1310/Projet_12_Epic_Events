from app.permissions.permissions import Permissions
from .contract_manage import ContractManage
from .customer_manage import CustomerManage
from .employee_manage import EmployeeManage
from .event_manage import EventManage
from .role_manage import RoleManage

class MenuManage:
    """
    Gère les menus et les actions associées dans l'application.

    Attributes:
        view: La vue utilisée pour afficher les menus.
        verify_jwt: La méthode de vérification du jeton JWT.
        delete_token: La méthode de suppression du jeton JWT.
        user_connect_id: L'ID de l'utilisateur connecté.
        employee_manage: L'instance de la gestion des employés.
        customer_manage: L'instance de la gestion des clients.
        contract_manage: L'instance de la gestion des contrats.
        event_manage: L'instance de la gestion des événements.
        role_manage: L'instance de la gestion des rôles.
        permissions: L'instance de la gestion des permissions.
    """

    def __init__(self, view, verify_jwt, delete_token, session, employee, role, logger):
        self.view = view
        self.session = session
        self.verify_jwt = verify_jwt
        self.delete_token = delete_token
        self.employee = employee
        self.role = role
        self.user_connected_id = employee.Id
        self.employee_manage = EmployeeManage(session, employee, role)
        self.customer_manage = CustomerManage(session, employee, role)
        self.contract_manage = ContractManage(session, employee, role)
        self.event_manage = EventManage(session, employee, role)
        self.role_manage = RoleManage(session, self.employee)
        self.permissions = Permissions()
        self.show_intro = False
        self.logger = logger
        self.is_logout = False


    def run(self):

        # décode le token
        decoded_payload = self.verify_jwt()

        # validation de l'authentification par rapport à l'utilisateur connecté
        if self.user_connected_id == decoded_payload["user_id"]:
            # affiche le menu principal
            self.menu_main()
        else:
            self.view.display_red_message("Authentification invalide pour cet utilisateur.")
            self.view.prompt_wait_enter()
            self.logout()

    def menu_main(self):
        """
        Composition du menu principal selon les permissions de l'utilisateur.
        """

        self.show_intro = True
        self.view.clear_screen()

        menu_items = ["Menu principal : ", {}]
        menu_items[1]["Gestion des clients"] = self.menu_customer
        menu_items[1]["Gestion des contrats"] = self.menu_contract
        menu_items[1]["Gestion des évènements"] = self.menu_event

        if self.permissions.can_read_employee(self.role):
            menu_items[1]["Gestion des employés"] = self.menu_employee

        if self.permissions.can_read_role(self.role):
            menu_items[1]["Gestion des permissions"] = self.menu_role

        menu_items[1]["Deconnexion"] = self.logout
        
        self.run_menu(menu_items, main=True)

    def menu_customer(self):
        """
        Composition du menu client selon les permissions de l'utilisateur.
        """

        menu_items = ["Gestion des Clients : ", {}]

        menu_items[1]["Liste des clients"] = self.customer_manage.list

        if self.permissions.role_name(self.role) == "Commercial":
            menu_items[1]["Liste de vos clients"] = self.customer_manage.list_yours_customers


        if self.permissions.can_update_customer(self.role):
            menu_items[1]["Modifier un client"] = self.customer_manage.update

        if self.permissions.can_create_delete_customer(self.role):
            menu_items[1]["Créer un client"] = self.customer_manage.create
            menu_items[1]["Supprimer un client"] = self.customer_manage.delete

        self.run_menu(menu_items, main=False)

    def menu_contract(self):
        """
        Composition du menu contrat selon les permissions de l'utilisateur..
        """

        menu_items = ["Gestion des Contrats : ", {}]

        menu_items[1]["Liste des contrats"] = self.contract_manage.list

        if self.permissions.role_name(self.role) == "Commercial":
            menu_items[1]["Liste de vos contrats"] = self.contract_manage.list_yours_contracts
            menu_items[1]["Liste de vos contrats non signés"] = self.contract_manage.list_yours_contracts_not_signed
            menu_items[1]["Liste de vos contrats non payés"] = self.contract_manage.list_yours_contracts_not_payed


        if self.permissions.can_update_contract(self.role):
            menu_items[1]["Modifier un contrat"] = self.contract_manage.update

        if self.permissions.can_create_delete_contract(self.role):
            menu_items[1]["Créer un contrat"] = self.contract_manage.create
            menu_items[1]["Supprimer un contrat"] = self.contract_manage.delete

        self.run_menu(menu_items, main=False)

    def menu_event(self):
        """
        Composition du menu évènement selon les permissions de l'utilisateur.
        """

        menu_items = ["Gestion des Evènements : ", {}]
        menu_items[1]["Liste des évènements"] = self.event_manage.list
        menu_items[1]["Liste des évènements sans support"] = self.event_manage.list_no_support

        if self.permissions.role_name(self.role) in ("Support", "Commercial"):
            menu_items[1]["Liste de vos évènements"] = self.event_manage.list_yours_events

        if self.permissions.can_update_event(self.role):
            menu_items[1]["Modifier un évènement"] = self.event_manage.update

        if self.permissions.can_create_delete_event(self.role):
            menu_items[1]["Créer un évènement"] = self.event_manage.create
            menu_items[1]["Supprimer un évènement"] = self.event_manage.delete

        self.run_menu(menu_items, main=False)

    def menu_employee(self):
        """
        Composition du menu employé selon les permissions de l'utilisateur.
        """

        menu_items = ["Gestion des Employés : ", {}]

        if self.permissions.can_read_employee(self.role):
            menu_items[1]["Liste des employés"] = self.employee_manage.list

        if self.permissions.can_update_employee(self.role):
            menu_items[1]["Modifier un employé"] = self.employee_manage.update

        if self.permissions.can_create_delete_employee(self.role):
            menu_items[1]["Créer un employé"] = self.employee_manage.create
            menu_items[1]["Supprimer un employé"] = self.employee_manage.delete

        self.run_menu(menu_items, main=False)

    def menu_role(self):
        """
        Composition du menu role selon les permissions de l'utilisateur.
        """

        menu_items = ["Gestion des Permissions : ", {}]

        if self.permissions.can_read_role(self.role):
            menu_items[1]["Liste des permissions"] = self.role_manage.list

        if self.permissions.can_update_role(self.role):
            menu_items[1]["Modifier une permission"] = self.role_manage.update

        if self.permissions.can_create_delete_role(self.role):
            menu_items[1]["Créer une permission"] = self.role_manage.create
            menu_items[1]["Supprimer une permission"] = self.role_manage.delete

        self.run_menu(menu_items, main=False)

    def run_menu(self, menu_items, main):
        """
        Gère l'affichage du menu et le choix de l'utilisateur.
        Lance la méthode associé à chaque menu.
        Déconnecte l'utilisateur si la session est expirée.

        Args:
            menu_items (tuple): Un tuple contenant le titre du menu et une liste de tuples contenant
            les éléments du menu sous forme de paires (index, nom_du_menu: méthode).

        """

        self.session.refresh(self.role)
    
        title = menu_items[0]

        # ajoute la ligne de retour selon le menu
        if not main:
            menu_items[1]["Retour au menu principal"] = self.menu_main

        # Crée la liste du menu indexée
        menu_list = []
        for index, menu in enumerate(menu_items[1], start=1):
            menu_list.append((index, menu))

        # vérifie la validité de la session
        while self.verify_jwt():

            user_connected = f"{self.employee.FirstName} {self.employee.LastName}"
            user_connected_status = self.employee.RoleRel.RoleName

            self.view.pass_n_lines()

            # affiche l'entete de l'application
            if self.show_intro:
                self.view.show_intro(user_connected, user_connected_status)
                self.show_intro = False

            # analyse du choix utilisateur
            choice = self.view.display_menu(title, menu_list)
            if choice.isdigit():
                choice = int(choice)
                for menu in menu_list:
                    if menu[0] == choice:
                        # Envoie vers la méthode choisie
                        menu_items[1][menu[1]]()
                  
            else:
                self.view.invalid_choice()
        
        if not self.verify_jwt() and not self.is_logout:
            self.logger.info(f"Session Expirée: {self.employee.Email}")
            self.logout()

            
    def logout(self):
        self.is_logout = True
        if self.session:
            self.session.close()
        self.delete_token()
        self.logger.info(f"Déconnexion: {self.employee.Email}")
        
        