import pytest
from unittest.mock import patch, Mock
from sqlalchemy.exc import IntegrityError, NoResultFound
from rich.table import Table
from datetime import datetime
from app.models.role import Role
from app.views.views import View
from app.controllers.role_manage import RoleManage


class TestRoleManage:
    """Tests unitaires pour la classe RoleManage"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.session = Mock()
        self.view = Mock()
        self.session.rollback = Mock()
        self.session.add = Mock()
        self.session.flush = Mock()
        self.session.commit = Mock()
        self.session.expunge = Mock()
        self.session.query = Mock()
        self.session.update = Mock()
        self.session.delete = Mock()
        self.role_manage = RoleManage(self.session)

        self.test_role = Role(
            Id=1,
            RoleName="Admin",
            Can_r_Employee=True,
            Can_ru_Employee=True,
            Can_crud_Employee=True,
            Can_r_Role=True,
            Can_ru_Role=True,
            Can_crud_Role=True,
            Can_ru_Customer=True,
            Can_crud_Customer=True,
            Can_access_all_Customer=True,
            Can_ru_Contract=True,
            Can_crud_Contract=True,
            Can_access_all_Contract=True,
            Can_ru_Event=True,
            Can_crud_Event=True,
            Can_access_all_Event=True,
            Can_access_support_Event=True,
            DateCreated=datetime(2023, 1, 1),
        )

        self.session.query.return_value.filter_by.return_value.one.return_value = self.test_role

        self.mock_role_class = patch("app.models.role.Role", autospec=True).start()
        self.mock_confirm_table_recap = patch.object(RoleManage, "confirm_table_recap").start()
        self.mock_return_choice = patch.object(View, "return_choice").start()
        self.mock_display_red_message = patch.object(View, "display_red_message").start()
        self.mock_display_green_message = patch.object(View, "display_green_message").start()
        self.mock_display_title_panel_color_fit = patch.object(View, "display_title_panel_color_fit").start()
        self.mock_display_table = patch.object(View, "display_table").start()
        self.mock_table_role_create = patch.object(RoleManage, "table_role_create").start()

        yield

        patch.stopall()

    # test méthode list

    def test_list(self):
        """Test de la méthode list()"""
        with patch.object(RoleManage, "filter") as mock_filter:

            # Arrangement
            mock_roles = [self.test_role]
            mock_filter.return_value = mock_roles
            mock_table = Mock()
            self.mock_table_role_create.return_value = mock_table

            # Action
            self.role_manage.list()

            # Assertions
            mock_filter.assert_called_once_with("All", None, Role)
            self.mock_table_role_create.assert_called_once_with(mock_roles)
            self.mock_display_table.assert_called_once_with(mock_table, "Liste des Roles")

    # test méthode create

    def test_create_success(self):
        """Test de la méthode create() avec succès"""
        role_name = "Admin"
        self.mock_return_choice.side_effect = [
            role_name,
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
        ]

        self.mock_confirm_table_recap.return_value = True

        # Appel de la méthode create()
        self.role_manage.create()

        # Vérification des appels et de la création du rôle
        self.mock_return_choice.assert_any_call("Entrez le nom du role ( vide pour annuler )", False)
        self.mock_return_choice.assert_any_call("Liste des employés ( 0:non(défaut) / 1:oui )", False, "0")
        self.mock_return_choice.assert_any_call("Modification des employés ( 0:non(défaut) / 1:oui )", False, "0")
        self.mock_return_choice.assert_any_call(
            "Création et Suppression des employés ( 0:non(défaut) / 1:oui )", False, "0"
        )
        self.mock_return_choice.assert_any_call("Liste des roles ( 0:non(défaut) / 1:oui )", False, "0")
        self.mock_return_choice.assert_any_call("Modification des roles ( 0:non(défaut) / 1:oui )", False, "0")
        self.mock_return_choice.assert_any_call(
            "Création et Suppression des roles ( 0:non(défaut) / 1:oui )", False, "0"
        )
        self.mock_return_choice.assert_any_call("Modification des clients ( 0:non(défaut) / 1:oui )", False, "0")
        self.mock_return_choice.assert_any_call(
            "Création et Suppression des clients ( 0:non(défaut) / 1:oui )", False, "0"
        )
        self.mock_return_choice.assert_any_call("Acces à tous les clients ( 0:non(défaut) / 1:oui )", False, "0")
        self.mock_return_choice.assert_any_call("Modification des contrats ( 0:non(défaut) / 1:oui )", False, "0")
        self.mock_return_choice.assert_any_call(
            "Création et Suppression des contrats ( 0:non(défaut) / 1:oui )", False, "0"
        )
        self.mock_return_choice.assert_any_call("Acces à tous les contrats ( 0:non(défaut) / 1:oui )", False, "0")
        self.mock_return_choice.assert_any_call("Modification des évènements ( 0:non(défaut) / 1:oui )", False, "0")
        self.mock_return_choice.assert_any_call(
            "Création et Suppression des évènements ( 0:non(défaut) / 1:oui )", False, "0"
        )
        self.mock_return_choice.assert_any_call("Acces à tous les évènements ( 0:non(défaut) / 1:oui )", False, "0")
        self.mock_return_choice.assert_any_call(
            "Accés au support des évènements ( 0:non(défaut) / 1:oui )", False, "0"
        )

        self.session.add.assert_called_once()
        added_role = self.session.add.call_args[0][0]  # Récupérer le premier argument (le rôle)

        assert added_role.RoleName == role_name
        self.session.commit.assert_called_once()

        # Vérification de la création du rôle avec les bonnes valeurs
        # mock_role_class.assert_called_once()

        self.mock_display_green_message.assert_called_once_with("\nRole créé avec succès !")
        self.mock_confirm_table_recap.assert_called_once()

    def test_create_cancelled_due_to_empty_role_name(self):
        """Test de la méthode create() lorsque le nom du rôle est vide"""

        self.mock_return_choice.side_effect = [
            "",  # role_name vide
        ]

        # Appel de la méthode create()
        self.role_manage.create()

        # Vérification des appels et de la création du rôle
        self.mock_return_choice.assert_any_call("Entrez le nom du role ( vide pour annuler )", False)

        # Vérification que le rôle n'est pas créé
        self.session.add.assert_not_called()
        self.session.commit.assert_not_called()
        self.mock_display_green_message.assert_not_called()
        self.mock_confirm_table_recap.assert_not_called()
        self.mock_role_class.assert_not_called()

    def test_create_cancelled_due_to_confirmation(self):
        """Test de la méthode create() lorsque la confirmation est annulée"""

        self.mock_return_choice.side_effect = [
            "Admin",  # role_name
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
        ]

        self.mock_confirm_table_recap.return_value = False

        # Appel de la méthode create()
        self.role_manage.create()

        # Vérification que le rôle n'est pas créé et est annulé correctement
        self.session.expunge.assert_called_once()  # Vérifie que expunge est appelé
        self.session.rollback.assert_called_once()  # Vérifie que rollback est appelé
        self.session.commit.assert_not_called()  # Vérifie que commit n'est pas appelé
        self.mock_display_green_message.assert_not_called()  # Vérifie que le message de succès n'est pas affiché
        self.mock_role_class.assert_not_called()  # Vérifie que le rôle est instancié

    def test_create_general_exception(self):
        """Test de la méthode create() avec une exception générale"""

        self.mock_return_choice.side_effect = [
            "Admin",  # role_name
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
        ]

        self.session.add.side_effect = Exception("General error")

        self.role_manage.create()

        self.session.rollback.assert_called_once()
        self.mock_display_red_message.assert_called_once_with("Erreur lors de la création du role : General error")

    def test_create_value_error(self):
        """Test de la méthode create() avec une ValueError"""

        self.mock_return_choice.side_effect = [
            "Admin",  # role_name
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
        ]

        self.session.add.side_effect = ValueError("Validation error")

        self.role_manage.create()

        self.session.rollback.assert_called_once()
        self.mock_display_red_message.assert_called_once_with("Erreur de validation : Validation error")

    def test_create_integrity_error(self):
        """Test de la méthode create() avec une IntegrityError"""

        self.mock_return_choice.side_effect = [
            "Admin",  # role_name
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
        ]

        self.session.add.side_effect = IntegrityError("Integrity error", "params", "orig")

        self.role_manage.create()

        self.session.rollback.assert_called_once()
        assert "Erreur :" in str(self.mock_display_red_message.call_args)

    # test méthode update

    def test_update_success(self):
        """Test de la méthode update() avec succès"""

        new_role_name = "New"
        self.mock_return_choice.side_effect = [
            str(self.test_role.Id),
            new_role_name,
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
        ]
        self.mock_confirm_table_recap.return_value = True

        # Appel de la méthode update()
        self.role_manage.update()

        # Vérification des appels et de la modification du rôle
        self.mock_display_title_panel_color_fit.assert_called_with("Modification d'un role", "yellow", True)
        self.session.query.assert_called_once_with(Role)
        self.session.query.return_value.filter_by.assert_called_once_with(Id=self.test_role.Id)
        self.session.commit.assert_called_once()

        assert self.test_role.RoleName == new_role_name

        self.mock_return_choice.assert_any_call("Entrez l'identifiant du role à modifier ( vide pour annuler )", False)
        # self.mock_return_choice.assert_any_call("Liste des employés", False, "1")
        # ... vérifier les autres appels

        self.mock_display_green_message.assert_called_once_with("\nRole modifié avec succès !")
        self.mock_confirm_table_recap.assert_called()

    def test_update_cancelled_due_to_empty_id(self):
        """Test de la méthode update() lorsque l' id du rôle est vide"""

        self.mock_return_choice.side_effect = [
            "",  # role_id vide
        ]

        # Appel de la méthode create()
        self.role_manage.update()

        # Vérification des appels et de la création du rôle
        self.mock_return_choice.assert_any_call("Entrez l'identifiant du role à modifier ( vide pour annuler )", False)

        # Vérification que le rôle n'est pas créé
        self.session.add.assert_not_called()
        self.session.commit.assert_not_called()
        self.mock_display_green_message.assert_not_called()
        self.mock_confirm_table_recap.assert_not_called()
        self.mock_role_class.assert_not_called()

    def test_update_bad_id_exception(self):
        """Test de la méthode update() avec un ID non valide"""

        self.mock_return_choice.side_effect = ["999", ""]
        self.session.query.return_value.filter_by.return_value.one.side_effect = NoResultFound

        self.role_manage.update()

        self.mock_display_red_message.assert_called_once_with("Identifiant non valide !")
        self.session.query.return_value.filter_by.assert_called_once_with(Id=999)

        # Vérification que la méthode return_choice a été appelée deux fois (une pour l'ID non valide, une pour l'annulation)
        assert self.mock_return_choice.call_count == 2

        self.session.add.assert_not_called()
        self.session.commit.assert_not_called()

    def test_update_cancelled_due_to_confirmation(self):
        """Test de la méthode update() avec annulation"""

        new_role_name = "New"
        self.mock_return_choice.side_effect = [
            str(self.test_role.Id),
            new_role_name,
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
        ]
        self.mock_confirm_table_recap.return_value = False
        self.role_manage.update()

        self.session.commit.assert_not_called()
        self.mock_display_green_message.assert_not_called()
        self.mock_role_class.assert_not_called()

    def test_update_integrity_error(self):
        """Test de la méthode update() avec une IntegrityError"""
        new_role_name = "New"
        self.mock_return_choice.side_effect = [
            str(self.test_role.Id),
            new_role_name,
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
        ]
        self.mock_confirm_table_recap.return_value = True
        self.session.commit.side_effect = IntegrityError("Integrity error", "params", "orig")

        # Appel de la méthode delete()
        self.role_manage.update()

        # Vérifications
        self.session.rollback.assert_called_once()
        assert "Erreur :" in str(self.mock_display_red_message.call_args)

    def test_update_value_error(self):
        """Test de la méthode update() avec une ValueError"""
        new_role_name = "New"
        self.mock_return_choice.side_effect = [
            str(self.test_role.Id),
            new_role_name,
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
        ]
        self.mock_confirm_table_recap.return_value = True
        self.session.commit.side_effect = ValueError("Validation error")

        # Appel de la méthode delete()
        self.role_manage.update()

        # Vérifications
        self.session.rollback.assert_called_once()
        assert "Validation error" in str(self.mock_display_red_message.call_args)

    def test_update_general_exception(self):
        """Test de la méthode update() avec une exception générale"""
        new_role_name = "New"
        self.mock_return_choice.side_effect = [
            str(self.test_role.Id),
            new_role_name,
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
        ]
        self.mock_confirm_table_recap.return_value = True
        self.session.commit.side_effect = Exception("Exception")

        # Appel de la méthode update()
        self.role_manage.update()

        # Vérifications
        self.session.rollback.assert_called_once()
        assert "Exception" in str(self.mock_display_red_message.call_args)

    # test méthode delete

    def test_delete_success(self):
        """Test de la méthode delete() avec succès"""
        role_id = str(self.test_role.Id)
        self.mock_return_choice.side_effect = [
            role_id,  # ID du rôle à supprimer     # Confirmation de la suppression
        ]

        self.mock_confirm_table_recap.return_value = True

        # Appel de la méthode delete()
        self.role_manage.delete()

        # Vérifications
        self.session.query.assert_called_once_with(Role)
        self.session.query.return_value.filter_by.assert_called_once_with(Id=int(role_id))
        self.session.delete.assert_called_once_with(self.test_role)
        self.session.commit.assert_called_once()
        self.mock_display_green_message.assert_called_once_with("Role supprimé avec succès !")

    def test_delete_cancelled_due_to_empty_id(self):
        """Test de la méthode delete() lorsque l'ID du rôle est vide"""
        self.mock_return_choice.return_value = ""  # ID vide

        # Appel de la méthode delete()
        self.role_manage.delete()

        # Vérifications
        self.session.query.assert_not_called()
        self.session.delete.assert_not_called()
        self.session.commit.assert_not_called()
        self.mock_display_green_message.assert_not_called()

    def test_delete_bad_id_exception(self):
        """Test de la méthode delete() avec un ID non valide"""
        self.mock_return_choice.side_effect = ["999", ""]  # ID non valide
        self.session.query.return_value.filter_by.side_effect = NoResultFound()

        # Appel de la méthode delete()
        self.role_manage.delete()

        # Vérifications
        self.mock_display_red_message.assert_called_once_with("Identifiant non valide !")
        assert self.mock_return_choice.call_count == 2

        self.session.add.assert_not_called()
        self.session.commit.assert_not_called()

    def test_delete_cancelled_due_to_confirmation(self):
        """Test de la méthode delete() avec annulation"""
        self.mock_return_choice.side_effect = [
            str(self.test_role.Id),  # ID du rôle à supprimer
            "no",  # Annulation de la suppression
        ]

        self.mock_confirm_table_recap.return_value = False

        # Appel de la méthode delete()
        self.role_manage.delete()

        # Vérifications
        self.session.delete.assert_not_called()
        self.session.commit.assert_not_called()
        self.mock_display_green_message.assert_not_called()

    def test_delete_integrity_error(self):
        """Test de la méthode delete() avec une IntegrityError"""
        self.mock_return_choice.side_effect = [
            str(self.test_role.Id),  # ID du rôle à supprimer
            "oui",  # Confirmation de la suppression
        ]
        self.session.delete.side_effect = IntegrityError("Integrity error", "params", "orig")

        # Appel de la méthode delete()
        self.role_manage.delete()

        # Vérifications
        self.session.rollback.assert_called_once()
        assert "Erreur :" in str(self.mock_display_red_message.call_args)

    def test_delete_general_exception(self):
        """Test de la méthode delete() avec une exception générale"""
        self.mock_return_choice.side_effect = [
            str(self.test_role.Id),  # ID du rôle à supprimer
            "yes",  # Confirmation de la suppression
        ]
        self.session.delete.side_effect = Exception("General error")

        # Appel de la méthode delete()
        self.role_manage.delete()

        # Vérifications
        self.session.rollback.assert_called_once()
        self.mock_display_red_message.assert_called_once_with("Erreur lors de la suppression du role : General error")

    # test méthode table_role_create

    def test_table_role_create(self):
        """Test de la méthode table_role_create()"""

        # self.mock_table_role_create.stop()
        patch.stopall()

        roles = [self.test_role, self.test_role]

        table = self.role_manage.table_role_create(roles)

        assert isinstance(table, Table)
        assert len(table.columns) == 19
        assert len(table.rows) == 2

    # test filter

    def test_filter_no_filtering(self):
        """Test de la méthode filter() sans filtrage"""
        self.session.query.return_value.all.return_value = [self.test_role]

        result = self.role_manage.filter("All", None, Role)

        self.session.query.assert_called_once_with(Role)
        self.session.query.return_value.all.assert_called_once()
        assert result == [self.test_role]

    def test_filter_with_filtering(self):
        """Test de la méthode filter() avec filtrage"""
        self.session.query.return_value.filter.return_value.all.return_value = [self.test_role]

        result = self.role_manage.filter("RoleName", "Admin", Role)

        self.session.query.assert_called_once_with(Role)
        self.session.query.return_value.filter.assert_called_once()
        self.session.query.return_value.all.assert_not_called()
        assert result == [self.test_role]

    def test_filter_with_filtering_valuenone(self):
        """Test de la méthode filter() avec filtrage et valeur Null"""
        self.session.query.return_value.filter.return_value.all.return_value = None

        result = self.role_manage.filter("RoleName", None, Role)

        self.session.query.assert_called_once_with(Role)
        self.session.query.return_value.filter.assert_called_once()
        self.session.query.return_value.all.assert_not_called()
        assert result is None

    # test format_date

    def test_format_date_with_valid_date(self):
        # Date valide
        test_date = datetime(2023, 6, 7, 15, 30)
        formatted_date = self.role_manage.format_date(test_date)
        assert formatted_date == "07/06/2023 15:30"

    # test confirm table

    def test_confirm_table_recap_confirmation_yes(self):
        """Test de la méthode confirm_table_recap avec confirmation 'oui'"""

        patch.stopall()

        with patch.object(View, "return_choice") as mock_return_choice, patch.object(
            View, "display_red_message"
        ) as mock_display_red_message, patch.object(
            View, "display_title_panel_color_fit"
        ) as mock_display_title_panel_color_fit, patch.object(
            View, "display_table"
        ) as mock_display_table, patch.object(
            RoleManage, "table_role_create"
        ) as mock_table_role_create:

            mock_return_choice.side_effect = ["oui"]

            mock_table = Mock()
            mock_table_role_create.return_value = mock_table

            role = self.test_role

            # Appel de la méthode confirm_table_recap
            result = self.role_manage.confirm_table_recap(role, "Suppression", "red")

            # Vérifications
            mock_display_title_panel_color_fit.assert_called_once_with("Suppression d'un role", "red", True)
            mock_display_table.assert_called_once()
            mock_return_choice.assert_called_once_with("Confirmation Suppression ? (oui/non)", False)
            mock_display_red_message.assert_not_called()
            assert result is True

    def test_confirm_table_recap_confirmation_no(self):
        """Test de la méthode confirm_table_recap avec annulation"""

        # self.mock_confirm_table_recap.stop()

        patch.stopall()

        with patch.object(View, "return_choice") as mock_return_choice, \
        patch.object(View, "display_red_message") as mock_display_red_message, \
        patch.object(View, "display_table") as mock_display_table, \
        patch.object(RoleManage, "table_role_create") as mock_table_role_create:

            mock_return_choice.side_effect = ["non"]
            mock_table = Mock()
            mock_display_table(mock_table)
            mock_table_role_create.return_value = mock_table

            role = self.test_role

            # Appel de la méthode confirm_table_recap
            result = self.role_manage.confirm_table_recap(role, "Suppression", "red")

            # Vérifications
            mock_display_red_message.assert_called()
            assert result is False


if __name__ == "__main__":
    pytest.main([__file__])
