from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String, func

from .database import Base


class Role(Base):
    """
    Représente un rôle dans la base de données.

    Attributes:
        Id (int): Identifiant unique du rôle.
        RoleName (str): Nom du rôle.
        Can_r_Employee (bool): Indique si le rôle peut lire les informations sur les employés.
        Can_ru_Employee (bool): Indique si le rôle peut lire et mettre à jour les informations sur les employés.
        Can_crud_Employee (bool): Indique si le rôle peut créer, lire, mettre à jour et supprimer les informations sur le employés.
        Can_r_role (bool): Indique si le rôle peut lire les informations sur les autres rôles.
        Can_ru_role (bool): Indique si le rôle peut lire et mettre à jour les informations sur les autres rôles.
        Can_crud_role (bool): Indique si le rôle peut créer, lire, mettre à jour et supprimer les informations sur les autres rôles.
        Can_r_Customer (bool): Indique si le rôle peut lire les informations sur les clients.
        Can_ru_customer (bool): Indique si le rôle peut lire et mettre à jour les informations sur les clients.
        Can_crud_Customer (bool): Indique si le rôle peut créer, lire, mettre à jour et supprimer les informations sur les clients.
        Can_r_Contract (bool): Indique si le rôle peut lire les informations sur les contrats.
        Can_ru_Contract (bool): Indique si le rôle peut lire et mettre à jour les informations sur les contrats.
        Can_crud_Contract (bool): Indique si le rôle peut créer, lire, mettre à jour et supprimer les informations sur les contrats.
        Can_r_Event (bool): Indique si le rôle peut lire les informations sur les événements.
        Can_ru_Event (bool): Indique si le rôle peut lire et mettre à jour les informations sur les événements.
        Can_crud_Event (bool): Indique si le rôle peut créer, lire, mettre à jour et supprimer les informations sur les événements.
        DateCreated (datetime): Date de création du rôle dans la base de données.
    """

    __tablename__ = "Role"

    Id = Column(Integer, primary_key=True)
    RoleName = Column(String(100), nullable=False, unique=True)
    Can_r_Employee = Column(Boolean, nullable=False, default=False)
    Can_ru_Employee = Column(Boolean, nullable=False, default=False)
    Can_crud_Employee = Column(Boolean, nullable=False, default=False)
    Can_r_Role = Column(Boolean, nullable=False, default=False)
    Can_ru_Role = Column(Boolean, nullable=False, default=False)
    Can_crud_Role = Column(Boolean, nullable=False, default=False)
    Can_r_Customer = Column(Boolean, nullable=False, default=False)
    Can_ru_Customer = Column(Boolean, nullable=False, default=False)
    Can_crud_Customer = Column(Boolean, nullable=False, default=False)
    Can_r_Contract = Column(Boolean, nullable=False, default=False)
    Can_ru_Contract = Column(Boolean, nullable=False, default=False)
    Can_crud_Contract = Column(Boolean, nullable=False, default=False)
    Can_r_Event = Column(Boolean, nullable=False, default=False)
    Can_ru_Event = Column(Boolean, nullable=False, default=False)
    Can_crud_Event = Column(Boolean, nullable=False, default=False)
    DateCreated = Column(TIMESTAMP, server_default=func.current_timestamp())
