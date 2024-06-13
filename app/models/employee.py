import re
from email.utils import parseaddr
import bcrypt
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship, validates

from .database import DatabaseConfig


class Employee(DatabaseConfig.BASE):
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
    PasswordHash = Column(String(255), nullable=False)
    RoleId = Column(Integer, ForeignKey("Role.Id", ondelete="SET NULL"))
    DateCreated = Column(TIMESTAMP, server_default=func.current_timestamp())

    RoleRel = relationship("Role", backref="EmployeesRel")

    @validates("Email")
    def validate_email(self, key, email):
        """
        Valide le format de l'email.

        Args:
            key (str): Clé de validation (Email).
            email (str): Adresse email à valider.

        Returns:
            str: L'adresse email en minuscules si elle est valide.

        Raises:
            ValueError: Si l'adresse email n'est pas valide.
        """
        _, parsed_email = parseaddr(email)
        if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", parsed_email):
            return email.lower()
        else:
            raise ValueError("Adresse email invalide")

    @validates("PasswordHash")
    def validate_password_hash(self, key, password):
        """
        Valide et hashe le mot de passe fourni.

        Args:
            key (str): Clé de validation (password_hash).
            password (str): Mot de passe à valider et hasher.

        Returns:
            str: Le hash du mot de passe.
        Raises:
            exceptions avec messages d'erreurs
        """

        # régles du mot de passe
        if not password:
            raise ValueError("Le mot de passe ne peut pas être vide")
        if len(password) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Le mot de passe doit contenir au moins une lettre majuscule")
        if not re.search(r"[a-z]", password):
            raise ValueError("Le mot de passe doit contenir au moins une lettre minuscule")
        if not re.search(r"\d", password):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre")

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # Postgre : Postgres comme DDBB et son driver, ou le système DDBB, encode toujours une chaîne déjà encodée.
        # Le deuxième processus d'encodage crée un hash invalide
        # Décoder d'abord le hash en utf8 avant de l'enregistrer dans le DDBB.

        return password_hash.decode("utf8")

    def verify_password(self, password):
        """
        Vérifie si le mot de passe fourni correspond au hash enregistré.

        Args:
            password (str): Mot de passe à vérifier.

        Returns:
            bool: True si le mot de passe correspond, False sinon.
        """
        return bcrypt.checkpw(password.encode("utf-8"), self.PasswordHash.encode("utf-8"))
