from typing import List, Type
from rich.table import Table
from sqlalchemy.exc import IntegrityError
from app.models.role import Role
from app.views.views import View

from .utils_manage import UtilsManage


class RoleManage:
    """
    Gère les opérations liées aux permissions, telles que l'affichage, la création, la mise à jour et la suppression.
    """

    def __init__(self, session):
        self.session = session
        self.view = View()
        self.utils = UtilsManage()

    def list(self):

        roles = self.utils.filter(self.session, "All", None, Role)
        table = self.utils.table_create("role", roles)
        self.view.display_table(table, "Liste des Roles")

    def create(self):
        self.view.display_title_panel_color_fit("Création d'un role", "green")

        # Collecte les informations sur le role
        role_name = self.view.return_choice("Entrez le nom du role ( vide pour annuler )", False)
        if not role_name:
            return

        r_employee = self.str_to_bool(
            self.view.return_choice("Liste des employés ( 0:non(défaut) / 1:oui )", False, "0")
        )
        ru_employee = self.str_to_bool(
            self.view.return_choice("Modification des employés ( 0:non(défaut) / 1:oui )", False, "0")
        )
        crud_employee = self.str_to_bool(
            self.view.return_choice("Création et Suppression des employés ( 0:non(défaut) / 1:oui )", False, "0")
        )
        r_role = self.str_to_bool(self.view.return_choice("Liste des roles ( 0:non(défaut) / 1:oui )", False, "0"))
        ru_role = self.str_to_bool(
            self.view.return_choice("Modification des roles ( 0:non(défaut) / 1:oui )", False, "0")
        )
        crud_role = self.str_to_bool(
            self.view.return_choice("Création et Suppression des roles ( 0:non(défaut) / 1:oui )", False, "0")
        )
        ru_customer = self.str_to_bool(
            self.view.return_choice("Modification des clients ( 0:non(défaut) / 1:oui )", False, "0")
        )
        crud_customer = self.str_to_bool(
            self.view.return_choice("Création et Suppression des clients ( 0:non(défaut) / 1:oui )", False, "0")
        )
        all_customer = self.str_to_bool(
            self.view.return_choice("Acces à tous les clients ( 0:non(défaut) / 1:oui )", False, "0")
        )
        ru_contract = self.str_to_bool(
            self.view.return_choice("Modification des contrats ( 0:non(défaut) / 1:oui )", False, "0")
        )
        crud_contract = self.str_to_bool(
            self.view.return_choice("Création et Suppression des contrats ( 0:non(défaut) / 1:oui )", False, "0")
        )
        all_contract = self.str_to_bool(
            self.view.return_choice("Acces à tous les contrats ( 0:non(défaut) / 1:oui )", False, "0")
        )
        ru_event = self.str_to_bool(
            self.view.return_choice("Modification des évènements ( 0:non(défaut) / 1:oui )", False, "0")
        )
        crud_event = self.str_to_bool(
            self.view.return_choice("Création et Suppression des évènements ( 0:non(défaut) / 1:oui )", False, "0")
        )
        all_event = self.str_to_bool(
            self.view.return_choice("Acces à tous les évènements ( 0:non(défaut) / 1:oui )", False, "0")
        )
        support_event = self.str_to_bool(
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

        # Ajouter à la session et commit
        try:
            self.session.add(role)
            self.session.flush()

            # Affichage et confirmation de la création
            if not self.utils.confirm_table_recap("role", role, "Création", "green"):
                self.session.expunge(role)
                self.session.rollback()
                return
            self.session.commit()
            self.view.display_green_message("\nRole créé avec succès !")
        except IntegrityError as e:
            self.session.rollback()
            error_detail = e
            self.view.display_red_message(f"Erreur : {error_detail}")
        except ValueError as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur de validation : {e}")
        except Exception as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur lors de la création du role : {e}")

    def update(self):
        self.view.display_title_panel_color_fit("Modification d'un role", "yellow")

        # Validation du role à modifier par son Id
        while True:
            role_id = self.view.return_choice("Entrez l'identifiant du role à modifier ( vide pour annuler )", False)

            if not role_id:
                return

            try:
                role = self.session.query(Role).filter_by(Id=int(role_id)).one()
                break
            except Exception:
                self.view.display_red_message("Identifiant non valide !")

        # Affichage et confirmation de la modification
        if not self.utils.confirm_table_recap("role", role, "Modification", "yellow"):
            return

        self.view.display_title_panel_color_fit("Modification d'un role", "yellow", True)
        role.RoleName = self.view.return_choice("Entrez le nom du role", False, f"{role.RoleName}")
        role.Can_r_Employee = self.str_to_bool(
            self.view.return_choice("Liste des employés", False, f"{role.Can_r_Employee}")
        )
        role.Can_ru_Employee = self.str_to_bool(
            self.view.return_choice("Modification des employés", False, f"{role.Can_ru_Employee}")
        )
        role.Can_crud_Employee = self.str_to_bool(
            self.view.return_choice("Création et Suppression des employés", False, f"{role.Can_crud_Employee}")
        )
        role.Can_r_Role = self.str_to_bool(self.view.return_choice("Liste des roles", False, f"{role.Can_r_Role}"))
        role.Can_ru_Role = self.str_to_bool(
            self.view.return_choice("Modification des roles", False, f"{role.Can_ru_Role}")
        )
        role.Can_crud_Role = self.str_to_bool(
            self.view.return_choice("Création et Suppression des roles", False, f"{role.Can_crud_Role}")
        )
        role.Can_ru_Customer = self.str_to_bool(
            self.view.return_choice("Modification des clients", False, f"{role.Can_ru_Customer}")
        )
        role.Can_crud_Customer = self.str_to_bool(
            self.view.return_choice("Création et Suppression des clients", False, f"{role.Can_crud_Customer}")
        )
        role.Can_access_all_Customer = self.str_to_bool(
            self.view.return_choice("Acces à tous les clients", False, f"{role.Can_access_all_Customer}")
        )
        role.Can_ru_Contract = self.str_to_bool(
            self.view.return_choice("Modification des contrats", False, f"{role.Can_ru_Contract}")
        )
        role.Can_crud_Contract = self.str_to_bool(
            self.view.return_choice("Création et Suppression des contrats", False, f"{role.Can_crud_Contract}")
        )
        role.Can_access_all_Contract = self.str_to_bool(
            self.view.return_choice("Acces à tous les contrats", False, f"{role.Can_access_all_Contract}")
        )
        role.Can_ru_Event = self.str_to_bool(
            self.view.return_choice("Modification des évènements", False, f"{role.Can_ru_Event}")
        )
        role.Can_crud_Event = self.str_to_bool(
            self.view.return_choice("Création et Suppression des évènements", False, f"{role.Can_crud_Event}")
        )
        role.Can_access_all_Event = self.str_to_bool(
            self.view.return_choice("Acces à tous les évènements", False, f"{role.Can_access_all_Event}")
        )
        role.Can_access_support_Event = self.str_to_bool(
            self.view.return_choice("Accés au support des évènements", False, f"{role.Can_access_support_Event}")
        )

        # Ajouter à la session et commit
        try:
            self.session.commit()

            # Affichage et confirmation de la modification
            if not self.utils.confirm_table_recap("role", role, "Modification", "yellow"):
                self.session.expunge(role)
                self.session.rollback()
                return

            self.view.display_green_message("\nRole modifié avec succès !")
        except IntegrityError as e:
            self.session.rollback()
            error_detail = e
            self.view.display_red_message(f"Erreur : {error_detail}")
        except ValueError as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur de validation : {e}")
        except Exception as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur lors de la création du role : {e}")

    def delete(self):
        self.view.display_title_panel_color_fit("Suppression d'un role", "red")

        # Validation du role à supprimer par son Id
        while True:
            role_id = self.view.return_choice("Entrez l'identifiant du role à supprimer ( vide pour annuler )", False)

            if not role_id:
                return

            try:
                role = self.session.query(Role).filter_by(Id=int(role_id)).one()
                break
            except Exception:
                self.view.display_red_message("Identifiant non valide !")

        # confirmation de la suppression
        if not self.utils.confirm_table_recap("role", role, "Suppression", "red"):
            return

        try:
            self.session.delete(role)
            self.session.commit()
            self.view.display_green_message("Role supprimé avec succès !")
        except IntegrityError as e:
            self.session.rollback()
            error_detail = e
            self.view.display_red_message(f"Erreur : {error_detail}")
        except Exception as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur lors de la suppression du role : {e}")

    def str_to_bool(self, str_value):

        if str_value.lower() in ("true", "1", "oui"):
            return True
        return False