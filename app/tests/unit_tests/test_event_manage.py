import pytest
from unittest.mock import patch, Mock
from datetime import datetime
from app.models.customer import Customer
from app.models.event import Event
from app.models.employee import Employee
from app.models.role import Role
from app.views.views import View
from app.controllers.event_manage import EventManage
from app.controllers.utils_manage import UtilsManage
from app.permissions.permissions import Permissions


class TestEventManage:
    """Tests unitaires pour la classe CustomerManage"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.session = Mock()
        self.customer = Mock(Customer)
        self.employee = Mock(Employee)
        self.role = Mock(Role)
        self.event_manage = EventManage(self.session, self.employee, self.role)

        self.test_event = Event(
            Id=1,
            ContractId=1,
            Title="Title",
            Notes="Notes",
            Location="Location",
            Attendees="10",
            DateCreated=datetime.now(),
        )

        self.mock_confirm_table_recap = patch.object(UtilsManage, "confirm_table_recap").start()
        self.mock_return_choice = patch.object(View, "return_choice").start()
        self.mock_display_red_message = patch.object(View, "display_red_message").start()
        self.mock_display_green_message = patch.object(View, "display_green_message").start()
        self.mock_display_title_panel_color_fit = patch.object(View, "display_title_panel_color_fit").start()
        self.mock_display_table = patch.object(View, "display_table").start()
        self.mock_table_create = patch.object(UtilsManage, "table_create").start()
        self.mock_filter = patch.object(UtilsManage, "filter").start()
        self.mock_valid_oper = patch.object(UtilsManage, "valid_oper").start()
        self.mock_valid_id = patch.object(UtilsManage, "valid_id").start()
        self.mock_permissions_role_name = patch.object(Permissions, "role_name").start()
        self.mock_permissions_all_event = patch.object(Permissions, "all_event").start()
        self.mock_permissions_all_contract = patch.object(Permissions, "all_contract").start()
        self.mock_get_permissions_events = patch.object(EventManage, "get_permissions_events").start()
        self.mock_get_permissions_contracts_signed = patch.object(
            EventManage, "get_permissions_contracts_signed"
        ).start()
        self.mock_validation_attendees = patch.object(EventManage, "validation_attendees").start()
        self.mock_validation_date = patch.object(EventManage, "validation_date").start()
        self.mock_valid_contract_id = patch.object(EventManage, "valid_contract").start()
        self.mock_permissions_can_access_support = patch.object(Permissions, "can_access_support").start()
        self.mock_valid_list = patch.object(EventManage, "valid_list").start()

        yield

        patch.stopall()

    # méthode list

    def test_list_success(self):

        # Arrang
        events = [Mock(), Mock()]
        self.mock_filter.return_value = events
        self.mock_table_create.return_value = Mock()

        # Act
        self.event_manage.list()

        # Assert
        self.mock_display_table.assert_called_once()

    def test_list_with_no_support(self):

        # Arrang
        events = [Mock(), Mock()]
        self.mock_filter.return_value = events
        self.mock_table_create.return_value = Mock()

        # Act
        self.event_manage.list_no_support()

        # Assert
        self.mock_display_table.assert_called_once()

    def test_list_yours_events(self):

        # Arrang
        events = [Mock(), Mock()]
        self.mock_get_permissions_events.return_value = events
        self.mock_table_create.return_value = Mock()

        # Act
        self.event_manage.list_yours_events()

        # Assert
        self.mock_get_permissions_events.assert_called_once()
        self.mock_display_table.assert_called_once()

    # méthode create

    def test_create_success(self):

        # Arrang
        contracts_signed = [Mock(), Mock()]
        self.mock_get_permissions_contracts_signed.return_value = contracts_signed
        self.mock_return_choice.side_effect = ["Title 1", "Notes", "Location"]
        self.mock_validation_attendees.return_value = 10
        self.mock_validation_date.return_value = ""
        self.mock_valid_contract_id.return_value = 1
        self.mock_permissions_can_access_support.return_value = True
        self.session.query.return_value.filter.return_value.one.return_value = Mock()
        self.mock_valid_list.return_value = 1

        # Act
        self.event_manage.create()

        # Assert
        self.mock_display_title_panel_color_fit.assert_called_with("Création d'un évènement", "green")
        self.mock_get_permissions_contracts_signed.assert_called_once()
        self.mock_valid_oper.assert_called_once()

    def test_create_with_no_contract_signed(self):

        # Arrang
        contracts_signed = []
        self.mock_get_permissions_contracts_signed.return_value = contracts_signed

        # Act
        self.event_manage.create()

        # Assert
        self.mock_display_title_panel_color_fit.assert_called_with("Création d'un évènement", "green")
        self.mock_get_permissions_contracts_signed.assert_called_once()
        self.mock_valid_oper.assert_not_called()

    def test_create_with_no_title(self):

        # Arrang
        contracts_signed = [Mock(), Mock()]
        self.mock_get_permissions_contracts_signed.return_value = contracts_signed
        self.mock_return_choice.side_effect = [""]

        # Act
        self.event_manage.create()

        # Assert
        self.mock_display_title_panel_color_fit.assert_called_with("Création d'un évènement", "green")
        self.mock_get_permissions_contracts_signed.assert_called_once()
        self.mock_valid_oper.assert_not_called()

    def test_create_with_no_contract_id(self):

        # Arrang
        contracts_signed = [Mock(), Mock()]
        self.mock_get_permissions_contracts_signed.return_value = contracts_signed
        self.mock_return_choice.side_effect = ["Title 1", "Notes", "Location"]
        self.mock_validation_attendees.return_value = 10
        self.mock_validation_date.return_value = ""
        self.mock_valid_contract_id.return_value = None
        self.mock_permissions_can_access_support.return_value = False

        # Act
        self.event_manage.create()

        # Assert
        self.mock_display_title_panel_color_fit.assert_called_with("Création d'un évènement", "green")
        self.mock_get_permissions_contracts_signed.assert_called_once()
        self.mock_valid_oper.assert_not_called()

    # methode update

    def test_update_success(self):

        # Arrang
        events = [Mock(), Mock()]
        self.mock_get_permissions_events.return_value = events
        contracts_signed = [Mock(), Mock()]
        self.mock_get_permissions_contracts_signed.return_value = contracts_signed
        self.mock_valid_id.return_value = Mock()
        self.mock_confirm_table_recap.return_value = True
        self.mock_return_choice.side_effect = ["Title", "Notes", "Location"]
        self.mock_validation_attendees.return_value = 10
        self.mock_validation_date = ""
        self.mock_permissions_can_access_support = True
        self.mock_valid_list.return_value = 1

        # Act
        self.event_manage.update()

        # Assert
        self.mock_display_title_panel_color_fit.assert_called_with("Modification d'un évènement", "yellow", True)
        self.mock_valid_oper.assert_called_once()

    def test_update_with_no_events(self):

        # Arrang
        events = []
        self.mock_get_permissions_events.return_value = events

        # Act
        self.event_manage.update()

        # Assert
        self.mock_display_red_message.assert_called_once_with("Vous n'avez aucuns évènements à modifier !!!")
        self.mock_valid_oper.assert_not_called()

    def test_update_with_no_event(self):

        # Arrang
        events = [Mock(), Mock()]
        self.mock_get_permissions_events.return_value = events
        contracts_signed = [Mock(), Mock()]
        self.mock_get_permissions_contracts_signed.return_value = contracts_signed
        self.mock_valid_id.return_value = None

        # Act
        self.event_manage.update()

        # Assert
        self.mock_valid_oper.assert_not_called()

    def test_update_with_no_validation(self):

        # Arrang
        events = [Mock(), Mock()]
        self.mock_get_permissions_events.return_value = events
        contracts_signed = [Mock(), Mock()]
        self.mock_get_permissions_contracts_signed.return_value = contracts_signed
        self.mock_valid_id.return_value = Mock()
        self.mock_confirm_table_recap.return_value = False

        # Act
        self.event_manage.update()

        # Assert
        self.mock_display_title_panel_color_fit.assert_called_with("Modification d'un évènement", "yellow")
        self.mock_valid_oper.assert_not_called()

    # méthode delete

    def test_delete_success(self):

        # Arrang
        events = [Mock(), Mock()]
        self.mock_get_permissions_events.return_value = events
        self.mock_valid_id.return_value = Mock()

        # Act
        self.event_manage.delete()

        # Assert
        self.mock_display_title_panel_color_fit.assert_called_with("Suppression d'un évènement", "red")
        self.mock_valid_oper.assert_called_once()

    def test_delete_with_no_events(self):

        # Arrang
        events = []
        self.mock_get_permissions_events.return_value = events

        # Act
        self.event_manage.delete()

        # Assert
        self.mock_display_red_message.assert_called_once_with("Vous n'avez aucuns évènements à supprimer !!!")
        self.mock_display_title_panel_color_fit.assert_called_with("Suppression d'un évènement", "red")
        self.mock_valid_oper.assert_not_called()

    def test_delete_with_no_event(self):

        # Arrang
        events = [Mock(), Mock()]
        self.mock_get_permissions_events.return_value = events
        self.mock_valid_id.return_value = None

        # Act
        self.event_manage.delete()

        # Assert
        self.mock_display_title_panel_color_fit.assert_called_with("Suppression d'un évènement", "red")
        self.mock_valid_oper.assert_not_called()

    def test_get_permissions_events(self):

        # Arrang 1 avec permission all_event
        patch.stopall()
        mock_filter = patch.object(UtilsManage, "filter").start()
        mock_permissions_all_event = patch.object(Permissions, "all_event").start()
        mock_permissions_role_name = patch.object(Permissions, "role_name").start()

        mock_permissions_all_event.return_value = True
        all_events = ["event 1", "event 2"]
        mock_filter.return_value = all_events

        # Act 1 avec permission all_event
        result = self.event_manage.get_permissions_events()

        # Assert 1 avec permission all_event
        assert result == all_events

        # Arrang 2 sans permissions all_event et role commercial
        mock_permissions_all_event.return_value = False
        mock_permissions_role_name.return_value = "Commercial"
        all_events_query = ["event 1", "event 2", "event 3"]
        self.session.query.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = (
            all_events_query
        )

        # Act 2 sans permissions all_event et role commercial
        result = self.event_manage.get_permissions_events()

        # Assert 2 sans permissions all_event et role commercial
        assert result == all_events_query

        # Arrang 3 sans permissions all_event et role support
        mock_permissions_role_name.return_value = "support"
        all_events_query = ["event 1"]
        self.session.query.return_value.filter.return_value.all.return_value = all_events_query

        # Act 3 sans permissions all_event et role support
        result = self.event_manage.get_permissions_events()

        # Assert 3 sans permissions all_event et role support
        assert result == all_events_query

        # Arrang 4 sans permissions all_event et autre role
        mock_permissions_role_name.return_value = "xxx"

        # Act 4 sans permissions all_event et autre role
        result = self.event_manage.get_permissions_events()

        # Assert 4 sans permissions all_event et autre role
        assert result == []

    def test_get_contracts_signed(self):

        # Arrang 1 avec permission all_contract
        patch.stopall()
        mock_filter = patch.object(UtilsManage, "filter").start()
        mock_permissions_all_contract = patch.object(Permissions, "all_contract").start()
        mock_permissions_role_name = patch.object(Permissions, "role_name").start()

        mock_permissions_all_contract.return_value = True
        all_contracts = ["contract 1", "contract 2"]
        mock_filter.return_value = all_contracts

        # Act 1 avec permission all_contract
        result = self.event_manage.get_permissions_contracts_signed()

        # Assert 1 avec permission all_contract
        assert result == all_contracts

        # Arrang 2 sans permissions all_contract et role commercial
        mock_permissions_all_contract.return_value = False
        mock_permissions_role_name.return_value = "Commercial"
        all_contracts_query = ["contract 1", "contract 2", "contract 3"]
        self.session.query.return_value.join.return_value.filter.return_value.filter.return_value.all.return_value = (
            all_contracts_query
        )

        # Act 2 sans permissions all_contract et role commercial
        result = self.event_manage.get_permissions_contracts_signed()

        # Assert 2 sans permissions all_contract et role commercial
        assert result == all_contracts_query

        # Arrang 3 sans permissions all_contract et autre role
        mock_permissions_role_name.return_value = "xxx"

        # Act 3 sans permissions all_contract et autre role
        result = self.event_manage.get_permissions_contracts_signed()

        # Assert 3 sans permissions all_contract et autre role
        assert result == []

    def test_validation_date(self):

        # Arrang 1 success
        patch.stopall()
        mock_return_choice = patch.object(View, "return_choice").start()
        mock_display_red_message = patch.object(View, "display_red_message").start()
        date = "01-01-2000"
        mock_return_choice.side_effect = [date]

        # Act 1 success
        result = self.event_manage.validation_date("DateStart", "message")

        # Assert 1 success
        assert result == date

        # Arrang 2 fail
        date = "2000/01/01"
        mock_return_choice.side_effect = [date, ""]

        # Act 2 fail
        self.event_manage.validation_date("DateStart", "message")

        # Assert 2 fail
        args, _ = mock_display_red_message.call_args
        assert "Erreur de validation :" in args[0]

    def test_validation_attendees(self):

        # Arrang 1 success
        patch.stopall()
        mock_return_choice = patch.object(View, "return_choice").start()
        mock_display_red_message = patch.object(View, "display_red_message").start()
        attendees = "20"
        mock_return_choice.side_effect = [attendees]

        # Act 1 success
        result = self.event_manage.validation_attendees("Attendees", "message")

        # Assert 1 sucess
        assert result == int(attendees)

        # Arrang 2 fail
        mock_return_choice.side_effect = ["xxx", "-100", ""]

        # Act 2 fail
        self.event_manage.validation_attendees("Attendees", "message")

        # Assert 2 fail
        args, _ = mock_display_red_message.call_args
        assert "Erreur de validation :" in args[0]



if __name__ == "__main__":
    pytest.main(["--cov=app/controllers/", "--cov-report=html", __file__])
