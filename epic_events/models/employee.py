from passlib.hash import bcrypt
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship, validates

from .database import Base


class Employee(Base):
    """
    Représente un employé dans la base de données.

    Attributes:
        Id (int): Identifiant unique de l'employé.
        FirstName (str): Prénom de l'employé.
        LastName (str): Nom de famille de l'employé.
        Email (str): Adresse e-mail de l'employé.
        PasswordHash (str): Hash du mot de passe de l'employé.
        RoleId (int): Identifiant du rôle de l'employé.
        DateCreated (datetime): Date de création de l'employé dans la base de données.
        Role (Role): Relation avec le rôle de l'employé.
    """

    __tablename__ = "Employee"

    Id = Column(Integer, primary_key=True, autoincrement=True)  # mettre index=True sur les champs ???
    FirstName = Column(String(100))
    LastName = Column(String(100))
    Email = Column(String(100), unique=True, nullable=False)
    PasswordHash = Column(String(100), nullable=False)
    RoleId = Column(Integer, ForeignKey("Role.Id", ondelete="RESTRICT"))
    DateCreated = Column(TIMESTAMP, server_default=func.current_timestamp())

    Role = relationship("Role", backref="Employees")

    @validates("PasswordHash")
    def validate_password_hash(self, key, password):
        """
        Valide et hashe le mot de passe fourni.

        Args:
            key (str): Clé de validation (password_hash).
            password (str): Mot de passe à valider et hasher.

        Returns:
            str: Le hash du mot de passe.
        """
        return bcrypt.hash(password)
