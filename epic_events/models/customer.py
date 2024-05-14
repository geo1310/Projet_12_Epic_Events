from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from .database import Base


class Customer(Base):
    """
    Représente un client dans la base de données.

    Attributes:
        Id (int): Identifiant unique du client.
        CommercialId (int): Identifiant du commercial associé au client.
        FirstName (str): Prénom du client.
        LastName (str): Nom de famille du client.
        Email (str): Adresse e-mail du client.
        PhoneNumber (str): Numéro de téléphone du client.
        Society (str): Nom de la société du client.
        DateCreated (datetime): Date de création du client dans la base de données.
        DateLastUpdate (datetime): Date de la dernière mise à jour du client dans la base de données.
        Commercial (Employee): Relation avec l'employé commercial associé.
    """

    __tablename__ = "Customer"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    CommercialId = Column(Integer, ForeignKey("Employee.Id", ondelete="RESTRICT"))
    FirstName = Column(String(100))
    LastName = Column(String(100))
    Email = Column(String(100), unique=True, nullable=False)
    PhoneNumber = Column(String(100))
    Society = Column(String(100))
    DateCreated = Column(TIMESTAMP, server_default=func.current_timestamp())
    DateLastUpdate = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    Commercial = relationship("Employee", backref="Customers")  # relation bidirectionnelles entre les classes
