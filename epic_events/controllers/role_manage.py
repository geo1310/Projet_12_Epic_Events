from rich.console import Console
from rich.table import Table
from sqlalchemy.exc import IntegrityError

from ..models.database import Session
from ..models.role import Role
from ..views.views import View


class RoleManage:
    """
    Gère les opérations liées aux permissions, telles que l'affichage, la création, la mise à jour et la suppression.
    """

    def __init__(self):
        self.session = Session()
        self.view = View()
        self.console = Console()

    def list(self):

        roles = self.session.query(Role).all()

        # création du tableau
        table = Table(show_header=True, header_style="bold green")
        # Ajouter des colonnes
        table.add_column("ID", style="dim", width=3)
        table.add_column("Nom")
        table.add_column("r_ employee")
        table.add_column("ru_ employee")
        table.add_column("crud employee")
        table.add_column("r_ role")
        table.add_column("ru_ role")
        table.add_column("crud role")
        table.add_column("r_ customer")
        table.add_column("all_ customer")
        table.add_column("ru_ customer")
        table.add_column("crud customer")
        table.add_column("r_ contract")
        table.add_column("all_ contract")
        table.add_column("ru_ contract")
        table.add_column("crud contract")
        table.add_column("r_ event")
        table.add_column("all_ event")
        table.add_column("ru_ event")
        table.add_column("crud event")
        table.add_column("Date de création")

        for role in roles:

            self.session.refresh(role)

            table.add_row(
                str(role.Id),
                role.RoleName,
                str(role.Can_r_Employee),
                str(role.Can_ru_Employee),
                str(role.Can_crud_Employee),
                str(role.Can_r_Role),
                str(role.Can_ru_Role),
                str(role.Can_crud_Role),
                str(role.Can_r_Customer),
                str(role.Can_access_all_Customer),
                str(role.Can_ru_Customer),
                str(role.Can_crud_Customer),
                str(role.Can_r_Contract),
                str(role.Can_access_all_Contract),
                str(role.Can_ru_Contract),
                str(role.Can_crud_Contract),
                str(role.Can_r_Event),
                str(role.Can_access_all_Event),
                str(role.Can_ru_Event),
                str(role.Can_crud_Event),
                self.format_date(role.DateCreated),
            )

        # Affiche le tableau
        self.view.display_table(table, "\nListe des Permissions")
        self.view.prompt_wait_enter()

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
        r_customer = self.str_to_bool(
            self.view.return_choice("Liste partielle des clients ( 0:non(défaut) / 1:oui )", False, "0")
        )
        all_customer = self.str_to_bool(
            self.view.return_choice("Liste Totale des clients ( 0:non(défaut) / 1:oui )", False, "0")
        )
        ru_customer = self.str_to_bool(
            self.view.return_choice("Modification des clients ( 0:non(défaut) / 1:oui )", False, "0")
        )
        crud_customer = self.str_to_bool(
            self.view.return_choice("Création et Suppression des clients ( 0:non(défaut) / 1:oui )", False, "0")
        )
        r_contract = self.str_to_bool(
            self.view.return_choice("Liste partielle des contrats ( 0:non(défaut) / 1:oui )", False, "0")
        )
        all_contract = self.str_to_bool(
            self.view.return_choice("Liste Totale des contrats ( 0:non(défaut) / 1:oui )", False, "0")
        )
        ru_contract = self.str_to_bool(
            self.view.return_choice("Modification des contrats ( 0:non(défaut) / 1:oui )", False, "0")
        )
        crud_contract = self.str_to_bool(
            self.view.return_choice("Création et Suppression des contrats ( 0:non(défaut) / 1:oui )", False, "0")
        )
        r_event = self.str_to_bool(
            self.view.return_choice("Liste partielle des évènements ( 0:non(défaut) / 1:oui )", False, "0")
        )
        all_event = self.str_to_bool(
            self.view.return_choice("Liste Totale des évènements ( 0:non(défaut) / 1:oui )", False, "0")
        )
        ru_event = self.str_to_bool(
            self.view.return_choice("Modification des évènements ( 0:non(défaut) / 1:oui )", False, "0")
        )
        crud_event = self.str_to_bool(
            self.view.return_choice("Création et Suppression des évènements ( 0:non(défaut) / 1:oui )", False, "0")
        )

        # Instance du nouveau role
        self.role = Role(
            RoleName=role_name,
            Can_r_Employee=r_employee,
            Can_ru_Employee=ru_employee,
            Can_crud_Employee=crud_employee,
            Can_r_Role=r_role,
            Can_ru_Role=ru_role,
            Can_crud_Role=crud_role,
            Can_r_Customer=r_customer,
            Can_access_all_Customer=all_customer,
            Can_ru_Customer=ru_customer,
            Can_crud_Customer=crud_customer,
            Can_r_Contract=r_contract,
            Can_access_all_Contract=all_contract,
            Can_ru_Contract=ru_contract,
            Can_crud_Contract=crud_contract,
            Can_r_Event=r_event,
            Can_access_all_Event=all_event,
            Can_ru_Event=ru_event,
            Can_crud_Event=crud_event,
        )

        # Ajouter à la session et commit
        try:
            self.session.add(self.role)
            self.session.flush()

            # Affichage et confirmation de la création
            if not self.confirm_table_recap("Création", "green"):
                self.session.expunge(self.role)
                self.session.rollback()
                return
            self.session.commit()
            self.view.display_green_message("\nRole créé avec succès !")
        except IntegrityError as e:
            self.session.rollback()
            error_detail = e.args[0].split("DETAIL:")[1] if e.args else "Erreur inconnue"
            self.view.display_red_message(f"Erreur : {error_detail}")
        except ValueError as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur de validation : {e}")
        except Exception as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur lors de la création du role : {e}")

        self.view.prompt_wait_enter()

    def update(self):
        self.view.display_title_panel_color_fit("Modification d'un role", "yellow")

        # Validation du role à modifier par son Id
        while True:
            role_id = self.view.return_choice("Entrez l'identifiant du role à modifier ( vide pour annuler )", False)

            if not role_id:
                return

            try:
                self.role = self.session.query(Role).filter_by(Id=int(role_id)).one()
                break
            except Exception:
                self.view.display_red_message("Identifiant non valide !")

        # Affichage et confirmation de la modification
        if not self.confirm_table_recap("Modification", "yellow"):
            return

        self.view.display_title_panel_color_fit("Modification d'un role", "yellow", True)
        self.role.RoleName = self.view.return_choice("Entrez le nom du role", False, f"{self.role.RoleName}")
        self.role.Can_r_Employee = self.str_to_bool(
            self.view.return_choice("Liste des employés", False, f"{self.role.Can_r_Employee}")
        )
        self.role.Can_ru_Employee = self.str_to_bool(
            self.view.return_choice("Modification des employés", False, f"{self.role.Can_ru_Employee}")
        )
        self.role.Can_crud_Employee = self.str_to_bool(
            self.view.return_choice("Création et Suppression des employés", False, f"{self.role.Can_crud_Employee}")
        )
        self.role.Can_r_Role = self.str_to_bool(
            self.view.return_choice("Liste des roles", False, f"{self.role.Can_r_Role}")
        )
        self.role.Can_ru_Role = self.str_to_bool(
            self.view.return_choice("Modification des roles", False, f"{self.role.Can_ru_Role}")
        )
        self.role.Can_crud_Role = self.str_to_bool(
            self.view.return_choice("Création et Suppression des roles", False, f"{self.role.Can_crud_Role}")
        )
        self.role.Can_r_Customer = self.str_to_bool(
            self.view.return_choice("Liste partielle des clients", False, f"{self.role.Can_r_Customer}")
        )
        self.role.Can_access_all_Customer = self.str_to_bool(
            self.view.return_choice("Liste Totale des clients", False, f"{self.role.Can_access_all_Customer}")
        )
        self.role.Can_ru_Customer = self.str_to_bool(
            self.view.return_choice("Modification des clients", False, f"{self.role.Can_ru_Customer}")
        )
        self.role.Can_crud_Customer = self.str_to_bool(
            self.view.return_choice("Création et Suppression des clients", False, f"{self.role.Can_crud_Customer}")
        )
        self.role.Can_r_Contract = self.str_to_bool(
            self.view.return_choice("Liste partielle des contrats", False, f"{self.role.Can_r_Contract}")
        )
        self.role.Can_access_all_Contract = self.str_to_bool(
            self.view.return_choice("Liste Totale des contrats", False, f"{self.role.Can_access_all_Contract}")
        )
        self.role.Can_ru_Contract = self.str_to_bool(
            self.view.return_choice("Modification des contrats", False, f"{self.role.Can_ru_Contract}")
        )
        self.role.Can_crud_Contract = self.str_to_bool(
            self.view.return_choice("Création et Suppression des contrats", False, f"{self.role.Can_crud_Contract}")
        )
        self.role.Can_r_Event = self.str_to_bool(
            self.view.return_choice("Liste partielle des évènements", False, f"{self.role.Can_r_Event}")
        )
        self.role.Can_access_all_Event = self.str_to_bool(
            self.view.return_choice("Liste Totale des évènements", False, f"{self.role.Can_access_all_Event}")
        )
        self.role.Can_ru_Event = self.str_to_bool(
            self.view.return_choice("Modification des évènements", False, f"{self.role.Can_ru_Event}")
        )
        self.role.Can_crud_Event = self.str_to_bool(
            self.view.return_choice("Création et Suppression des évènements", False, f"{self.role.Can_crud_Event}")
        )

        # Ajouter à la session et commit
        try:
            self.session.commit()

            # Affichage et confirmation de la modification
            if not self.confirm_table_recap("Modification", "yellow"):
                self.session.expunge(self.role)
                self.session.rollback()
                return

            self.view.display_green_message("\nRole modifié avec succès !")
        except IntegrityError as e:
            self.session.rollback()
            error_detail = e.args[0].split("DETAIL:")[1] if e.args else "Erreur inconnue"
            self.view.display_red_message(f"Erreur : {error_detail}")
        except ValueError as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur de validation : {e}")
        except Exception as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur lors de la création du role : {e}")

        self.view.prompt_wait_enter()

    def delete(self):
        self.view.display_title_panel_color_fit("Suppression d'un role", "red")

        # Validation du role à supprimer par son Id
        while True:
            role_id = self.view.return_choice("Entrez l'identifiant du role à supprimer ( vide pour annuler )", False)

            if not role_id:
                return

            try:
                self.role = self.session.query(Role).filter_by(Id=int(role_id)).one()
                break
            except Exception:
                self.view.display_red_message("Identifiant non valide !")

        # confirmation de la suppression
        if not self.confirm_table_recap("Suppression", "red"):
            return

        try:
            self.session.delete(self.role)
            self.session.commit()
            self.view.display_green_message("Role supprimé avec succès !")
        except IntegrityError as e:
            self.session.rollback()
            error_detail = e.args[0].split("DETAIL:")[1] if e.args else "Erreur inconnue"
            self.view.display_red_message(f"Erreur : {error_detail}")
        except Exception as e:
            self.session.rollback()
            self.view.display_red_message(f"Erreur lors de la suppression du role : {e}")

        self.view.prompt_wait_enter()

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

    def confirm_table_recap(self, oper: str, color: str = "white"):
        """
        Affiche un tableau récapitulatif des informations du role et demande une confirmation.

        Cette méthode crée et affiche un tableau récapitulatif contenant les informations du role.
        Ensuite, elle demande à l'utilisateur de confirmer l'opération en saisissant 'oui' ou 'non'.
        Si l'utilisateur confirme, la méthode retourne True.

        Args:
        oper (str): L'opération à confirmer (par exemple, 'Création', 'Mise à jour', 'Suppression').
        color (str): Couleur du texte

        Returns:
            bool: True si l'utilisateur confirme l'opération, False sinon.

        """

        self.view.display_title_panel_color_fit(f"{oper} d'un role", f"{color}", True)

        # Tableau récapitulatif
        table = Table()
        table.add_column("ID", style="dim", width=3)
        table.add_column("Nom")
        table.add_column("r_ employee")
        table.add_column("ru_ employee")
        table.add_column("crud employee")
        table.add_column("r_ role")
        table.add_column("ru_ role")
        table.add_column("crud role")
        table.add_column("r_ customer")
        table.add_column("all_ customer")
        table.add_column("ru_ customer")
        table.add_column("crud customer")
        table.add_column("r_ contract")
        table.add_column("all_ contract")
        table.add_column("ru_ contract")
        table.add_column("crud contract")
        table.add_column("r_ event")
        table.add_column("all_ event")
        table.add_column("ru_ event")
        table.add_column("crud event")
        table.add_column("Date de création")
        table.add_row(
            str(self.role.Id),
            self.role.RoleName,
            str(self.role.Can_r_Employee),
            str(self.role.Can_ru_Employee),
            str(self.role.Can_crud_Employee),
            str(self.role.Can_r_Role),
            str(self.role.Can_ru_Role),
            str(self.role.Can_crud_Role),
            str(self.role.Can_r_Customer),
            str(self.role.Can_access_all_Customer),
            str(self.role.Can_ru_Customer),
            str(self.role.Can_crud_Customer),
            str(self.role.Can_r_Contract),
            str(self.role.Can_access_all_Contract),
            str(self.role.Can_ru_Contract),
            str(self.role.Can_crud_Contract),
            str(self.role.Can_r_Event),
            str(self.role.Can_access_all_Event),
            str(self.role.Can_ru_Event),
            str(self.role.Can_crud_Event),
            self.format_date(self.role.DateCreated),
        )

        self.view.display_table(table, "Résumé du role")

        # Demander une confirmation avant validation
        confirm = self.view.return_choice(f"Confirmation {oper} ? (oui/non)", False)
        if confirm:
            confirm = confirm.lower()
        if confirm != "oui":
            self.view.display_red_message("Opération annulée.")
            self.view.prompt_wait_enter()
            return False
        return True

    def str_to_bool(self, str_value):

        if str_value.lower() in ("true", "1", "oui"):
            return True
        return False
