import sys

from ..models.database import Session
from ..models.employee import Employee
from ..models.role import Role
from ..permissions.permissions import Permissions
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

    def __init__(self, view, verify_jwt, delete_token, user_connected_id):
        self.view = view
        self.verify_jwt = verify_jwt
        self.delete_token = delete_token
        self.user_connected_id = user_connected_id
        self.employee_manage = EmployeeManage()
        self.customer_manage = CustomerManage(user_connected_id)
        self.contract_manage = ContractManage(user_connected_id)
        self.event_manage = EventManage()
        self.role_manage = RoleManage()
        self.permissions = Permissions()

    def run(self):

        # décode le token
        decoded_payload = self.verify_jwt()

        # validation de l'authentification par rapport à l'utilisateur connecté
        if self.user_connected_id == decoded_payload["user_id"]:

            # crée l'instance de l'utilisateur connecté
            self.session = Session()
            self.employee = self.session.query(Employee).filter_by(Id=self.user_connected_id).one()
            self.role = self.session.query(Role).filter_by(Id=self.employee.RoleId).one()

            # affiche le menu principal
            self.main_menu()
        else:
            self.view.display_red_message("Authentification invalide pour cet utilisateur.")
            self.quit_app()

    def main_menu(self):
        """
        Composition du menu principal selon les permissions de l'utilisateur.
        """

        menu_items = ["Menu principal : ", {}]

        if self.permissions.can_read_customer(self.role):
            menu_items[1]["Gestion des clients"] = self.menu_customer

        if self.permissions.can_read_contract(self.role):
            menu_items[1]["Gestion des contrats"] = self.menu_contract

        if self.permissions.can_read_event(self.role):
            menu_items[1]["Gestion des évènements"] = self.menu_event

        if self.permissions.can_read_employee(self.role):
            menu_items[1]["Gestion des employés"] = self.menu_employee

        if self.permissions.can_read_role(self.role):
            menu_items[1]["Gestion des permissions"] = self.menu_role

        self.run_menu(menu_items, main=True)

    def menu_customer(self):
        """
        Composition du menu client selon les permissions de l'utilisateur.
        """
        menu_items = ["Gestion des Clients : ", {}]

        if self.permissions.can_read_customer(self.role):
            menu_items[1]["Liste des clients"] = self.customer_manage.list

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

        if self.permissions.can_read_contract(self.role):
            menu_items[1]["Liste des contrats"] = self.contract_manage.list

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

        if self.permissions.can_read_event(self.role):
            menu_items[1]["Liste des évènements"] = self.event_manage.list

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
        self.view.clear_screen()
        title = menu_items[0]

        # ajoute la ligne de retour selon le menu
        if main:
            menu_items[1]["Quitter"] = self.quit_app
        else:
            menu_items[1]["Retour au menu principal"] = self.main_menu

        # Crée la liste du menu indexée
        menu_list = []
        for index, menu in enumerate(menu_items[1], start=1):
            menu_list.append((index, menu))

        # vérifie la validité de la session
        while self.verify_jwt():

            user_connected = f"{self.employee.FirstName} {self.employee.LastName}"
            user_connected_status = self.employee.RoleRel.RoleName

            # affiche l'entete de l'application
            self.view.show_intro(user_connected, user_connected_status)

            # analyse du choix utilisateur
            choice = self.view.display_menu(title, menu_list)
            if choice.isdigit():
                choice = int(choice)
                for menu in menu_list:
                    if menu[0] == choice:
                        # Envoie vers la méthode choisie avec l id de l'utilisateur connecté
                        menu_items[1][menu[1]]()
                    self.view.clear_screen()

            else:
                self.view.invalid_choice()
                self.view.prompt_wait_enter()
                self.view.clear_screen()

        self.view.display_red_message("Votre session a expirée, veuillez vous re-connecter.\n")
        self.quit_app()

    def quit_app(self):
        """
        Quitte l'application en supprimant le jeton JWT et en arrêtant le script.
        """
        if self.session:
            self.session.close()
        self.delete_token()
        sys.exit()
