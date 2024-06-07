from typing import List, Type
from rich.table import Table
from sqlalchemy.exc import IntegrityError
from app.models.role import Role
from app.views.views import View


class RoleManage:
    """
    Gère les opérations liées aux permissions, telles que l'affichage, la création, la mise à jour et la suppression.
    """

    def __init__(self, session):
        self.session = session
        self.view = View()

    def list(self):

        roles = self.filter("All", None, Role)
        table = self.table_role_create(roles)
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
            if not self.confirm_table_recap(role, "Création", "green"):
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
        if not self.confirm_table_recap(role, "Modification", "yellow"):
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
        role.Can_r_Role = self.str_to_bool(
            self.view.return_choice("Liste des roles", False, f"{role.Can_r_Role}")
        )
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
            if not self.confirm_table_recap(role, "Modification", "yellow"):
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
        if not self.confirm_table_recap(role, "Suppression", "red"):
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

    def confirm_table_recap(self, role: Role, oper: str, color: str = "white"):
        
        self.view.display_title_panel_color_fit(f"{oper} d'un role", f"{color}", True)

        # Tableau récapitulatif
        table = self.table_role_create([role])

        self.view.display_table(table, "Résumé du role")

        # Demander une confirmation avant validation
        confirm = self.view.return_choice(f"Confirmation {oper} ? (oui/non)", False)
        if confirm:
            confirm = confirm.lower()
        if confirm != "oui":
            self.view.display_red_message("Opération annulée.")
            return False
        return True

    def str_to_bool(self, str_value):

        if str_value.lower() in ("true", "1", "oui"):
            return True
        return False
    
    def table_role_create(self, roles: List[Role]) -> Table:
        """
        Crée un tableau pour afficher les roles.

        Cette méthode prend une liste d'événements en entrée et génère un tableau contenant les détails de chaque événement
        pour affichage.

        Args:
            roles (List[Role]): Une liste d'objets Role à afficher dans le tableau.

        Returns:
            Table: Un objet Table de la bibliothèque Rich contenant les informations des événements.
        """

        # Création du tableau pour afficher les événements
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
    
    
