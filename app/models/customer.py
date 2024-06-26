import re
from email.utils import parseaddr

from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship, validates

from app.models.employee import Employee

from .database import DatabaseConfig


class Customer(DatabaseConfig.BASE):
    """
    Représente un client dans la base de données.

    Attributes:
        Id (int): Identifiant unique du client.
        CommercialId (int): Identifiant du commercial associé au client.
        FirstName (str): Prénom du client.
        LastName (str): Nom de famille du client.
        Email (str): Adresse e-mail du client.
        PhoneNumber (str): Numéro de téléphone du client.
        Company (str): Nom de la société du client.
        DateCreated (datetime): Date de création du client dans la base de données.
        DateLastUpdate (datetime): Date de la dernière mise à jour du client dans la base de données.
        Commercial (Employee): Relation avec l'employé commercial associé.
    """

    __tablename__ = "Customer"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    CommercialId = Column(Integer, ForeignKey("Employee.Id", ondelete="CASCADE"), nullable=False)
    FirstName = Column(String(100))
    LastName = Column(String(100))
    Email = Column(String(100), unique=True, nullable=False)
    PhoneNumber = Column(String(100))
    Company = Column(String(100))
    DateCreated = Column(TIMESTAMP, server_default=func.current_timestamp())
    DateLastUpdate = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    CommercialRel = relationship("Employee", backref="CustomersRel")  # relation bidirectionnelles entre les classes

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
