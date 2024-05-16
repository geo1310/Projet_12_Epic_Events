class Permissions:
    """
    Classe pour gérer les autorisations.
    """

    @staticmethod
    def can_read_employee(role):
        if role.Can_r_Employee or role.Can_ru_Employee or role.Can_crud_Employee:
            return True
        else:
            return False

    @staticmethod
    def can_update_employee(role):
        if role.Can_ru_Employee or role.Can_crud_Employee:
            return True
        else:
            return False

    @staticmethod
    def can_create_delete_employee(role):
        return role.Can_crud_Employee

    @staticmethod
    def can_read_role(role):
        if role.Can_r_Role or role.Can_ru_Role or role.Can_crud_Role:
            return True
        else:
            return False

    @staticmethod
    def can_update_role(role):
        if role.Can_ru_Role or role.Can_crud_Role:
            return True
        else:
            return False

    @staticmethod
    def can_create_delete_role(role):
        return role.Can_crud_Role

    @staticmethod
    def can_read_customer(role):
        if role.Can_r_Customer or role.Can_ru_Customer or role.Can_crud_Customer:
            return True
        else:
            return False

    @staticmethod
    def can_update_customer(role):
        if role.Can_ru_Customer or role.Can_crud_Customer:
            return True
        else:
            return False

    @staticmethod
    def can_create_delete_customer(role):
        return role.Can_crud_Customer

    @staticmethod
    def can_read_contract(role):
        if role.Can_r_Contract or role.Can_ru_Contract or role.Can_crud_Contract:
            return True
        else:
            return False

    @staticmethod
    def can_update_contract(role):
        if role.Can_ru_Contract or role.Can_crud_Contract:
            return True
        else:
            return False

    @staticmethod
    def can_create_delete_contract(role):
        return role.Can_crud_Contract

    @staticmethod
    def can_read_event(role):
        if role.Can_r_Event or role.Can_ru_Event or role.Can_crud_Event:
            return True
        else:
            return False

    @staticmethod
    def can_update_event(role):
        if role.Can_ru_Event or role.Can_crud_Event:
            return True
        else:
            return False

    @staticmethod
    def can_create_delete_event(role):
        return role.Can_crud_Event
