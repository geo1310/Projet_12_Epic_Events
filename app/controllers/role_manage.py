from models.role import Role
from views.views import View

from .utils_manage import UtilsManage


class RoleManage:
    """
    Gère les opérations liées aux permissions, telles que l'affichage, la création, la mise à jour et la suppression.
    """

    def __init__(self, session, employee):
        self.session = session
        self.view = View()
        self.employee = employee
        self.utils = UtilsManage(self.employee)

    def list(self) -> None:
        """
        Affiche la liste des rôles.
        """

        roles = self.utils.filter(self.session, "All", None, Role)
        table = self.utils.table_create("role", roles)
        self.view.display_table(table, "Liste des Roles")

    def create(self) -> None:
        """
        Crée un nouveau rôle.
        """

        self.view.display_title_panel_color_fit("Création d'un role", "green")

        # Collecte les informations sur le role
        role_name = self.view.return_choice("Entrez le nom du role ( vide pour annuler )", False)
        if not role_name:
            return

        r_employee = self.utils.str_to_bool(
            self.view.return_choice("Liste des employés ( 0:non(défaut) / 1:oui )", False, "0")
        )
        ru_employee = self.utils.str_to_bool(
            self.view.return_choice("Modification des employés ( 0:non(défaut) / 1:oui )", False, "0")
        )
        crud_employee = self.utils.str_to_bool(
            self.view.return_choice("Création et Suppression des employés ( 0:non(défaut) / 1:oui )", False, "0")
        )
        r_role = self.utils.str_to_bool(
            self.view.return_choice("Liste des roles ( 0:non(défaut) / 1:oui )", False, "0")
        )
        ru_role = self.utils.str_to_bool(
            self.view.return_choice("Modification des roles ( 0:non(défaut) / 1:oui )", False, "0")
        )
        crud_role = self.utils.str_to_bool(
            self.view.return_choice("Création et Suppression des roles ( 0:non(défaut) / 1:oui )", False, "0")
        )
        ru_customer = self.utils.str_to_bool(
            self.view.return_choice("Modification des clients ( 0:non(défaut) / 1:oui )", False, "0")
        )
        crud_customer = self.utils.str_to_bool(
            self.view.return_choice("Création et Suppression des clients ( 0:non(défaut) / 1:oui )", False, "0")
        )
        all_customer = self.utils.str_to_bool(
            self.view.return_choice("Acces à tous les clients ( 0:non(défaut) / 1:oui )", False, "0")
        )
        ru_contract = self.utils.str_to_bool(
            self.view.return_choice("Modification des contrats ( 0:non(défaut) / 1:oui )", False, "0")
        )
        crud_contract = self.utils.str_to_bool(
            self.view.return_choice("Création et Suppression des contrats ( 0:non(défaut) / 1:oui )", False, "0")
        )
        all_contract = self.utils.str_to_bool(
            self.view.return_choice("Acces à tous les contrats ( 0:non(défaut) / 1:oui )", False, "0")
        )
        ru_event = self.utils.str_to_bool(
            self.view.return_choice("Modification des évènements ( 0:non(défaut) / 1:oui )", False, "0")
        )
        crud_event = self.utils.str_to_bool(
            self.view.return_choice("Création et Suppression des évènements ( 0:non(défaut) / 1:oui )", False, "0")
        )
        all_event = self.utils.str_to_bool(
            self.view.return_choice("Acces à tous les évènements ( 0:non(défaut) / 1:oui )", False, "0")
        )
        support_event = self.utils.str_to_bool(
            self.view.return_choice("Accés au support des évènements ( 0:non(défaut) / 1:oui )", False, "0")
        )

        # Instance du nouveau role
        role = Role(
            RoleName=role_name,
            Can_r_Employee=r_employee,
            Can_ru_Employee=ru_employee,
            Can_crud_Employee=crud_employee,
            Can_r_Role=r_role,
            Can_ru_Role=ru_role,
            Can_crud_Role=crud_role,
            Can_ru_Customer=ru_customer,
            Can_crud_Customer=crud_customer,
            Can_access_all_Customer=all_customer,
            Can_ru_Contract=ru_contract,
            Can_crud_Contract=crud_contract,
            Can_access_all_Contract=all_contract,
            Can_ru_Event=ru_event,
            Can_crud_Event=crud_event,
            Can_access_all_Event=all_event,
            Can_access_support_Event=support_event,
        )

        self.utils.valid_oper(self.session, "role", "create", role)

    def update(self) -> None:
        """
        Modifie un rôle existant.
        """

        self.view.display_title_panel_color_fit("Modification d'un role", "yellow")

        # Validation du role à modifier par son Id
        role = self.utils.valid_id(self.session, Role, "role à modifier")
        if not role:
            return

        # Affichage et confirmation de la modification
        if not self.utils.confirm_table_recap("role", role, "Modification", "yellow"):
            return

        self.view.display_title_panel_color_fit("Modification d'un role", "yellow", True)
        role.RoleName = self.view.return_choice("Entrez le nom du role", False, f"{role.RoleName}")
        role.Can_r_Employee = self.utils.str_to_bool(
            self.view.return_choice("Liste des employés", False, f"{role.Can_r_Employee}")
        )
        role.Can_ru_Employee = self.utils.str_to_bool(
            self.view.return_choice("Modification des employés", False, f"{role.Can_ru_Employee}")
        )
        role.Can_crud_Employee = self.utils.str_to_bool(
            self.view.return_choice("Création et Suppression des employés", False, f"{role.Can_crud_Employee}")
        )
        role.Can_r_Role = self.utils.str_to_bool(
            self.view.return_choice("Liste des roles", False, f"{role.Can_r_Role}")
        )
        role.Can_ru_Role = self.utils.str_to_bool(
            self.view.return_choice("Modification des roles", False, f"{role.Can_ru_Role}")
        )
        role.Can_crud_Role = self.utils.str_to_bool(
            self.view.return_choice("Création et Suppression des roles", False, f"{role.Can_crud_Role}")
        )
        role.Can_ru_Customer = self.utils.str_to_bool(
            self.view.return_choice("Modification des clients", False, f"{role.Can_ru_Customer}")
        )
        role.Can_crud_Customer = self.utils.str_to_bool(
            self.view.return_choice("Création et Suppression des clients", False, f"{role.Can_crud_Customer}")
        )
        role.Can_access_all_Customer = self.utils.str_to_bool(
            self.view.return_choice("Acces à tous les clients", False, f"{role.Can_access_all_Customer}")
        )
        role.Can_ru_Contract = self.utils.str_to_bool(
            self.view.return_choice("Modification des contrats", False, f"{role.Can_ru_Contract}")
        )
        role.Can_crud_Contract = self.utils.str_to_bool(
            self.view.return_choice("Création et Suppression des contrats", False, f"{role.Can_crud_Contract}")
        )
        role.Can_access_all_Contract = self.utils.str_to_bool(
            self.view.return_choice("Acces à tous les contrats", False, f"{role.Can_access_all_Contract}")
        )
        role.Can_ru_Event = self.utils.str_to_bool(
            self.view.return_choice("Modification des évènements", False, f"{role.Can_ru_Event}")
        )
        role.Can_crud_Event = self.utils.str_to_bool(
            self.view.return_choice("Création et Suppression des évènements", False, f"{role.Can_crud_Event}")
        )
        role.Can_access_all_Event = self.utils.str_to_bool(
            self.view.return_choice("Acces à tous les évènements", False, f"{role.Can_access_all_Event}")
        )
        role.Can_access_support_Event = self.utils.str_to_bool(
            self.view.return_choice("Accés au support des évènements", False, f"{role.Can_access_support_Event}")
        )

        self.utils.valid_oper(self.session, "role", "update", role)

    def delete(self) -> None:
        """
        Supprime un rôle existant.

        Cette méthode permet de supprimer un rôle de la base de données en demandant à l'utilisateur
        de saisir un identifiant de rôle, puis de valider la suppression.
        """

        self.view.display_title_panel_color_fit("Suppression d'un role", "red")

        # Validation du role à supprimer par son Id
        role = self.utils.valid_id(self.session, Role, "role à supprimer")
        if not role:
            return

        self.utils.valid_oper(self.session, "role", "delete", role)
