from sqlalchemy import (TIMESTAMP, Boolean, Column, Float, ForeignKey, Integer,
                        String, func)
from sqlalchemy.orm import relationship

from epic_events.models.customer import Customer

from .database import Base


class Contract(Base):
    """
    Représente un contrat dans la base de données.

    Attributes:
        Id (int): Identifiant unique du contrat.
        CustomerId (int): Identifiant du client associé au contrat.
        Title (str): Titre du contrat.
        Amount (float): Montant total du contrat.
        AmountOutstanding (float): Montant restant à payer pour le contrat.
        ContractSigned (bool): Indique si le contrat est signé ou non.
        DateCreated (datetime): Date de création du contrat dans la base de données.
        Customer (Customer): Relation avec le client associé.
    """

    __tablename__ = "Contract"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    CustomerId = Column(Integer, ForeignKey("Customer.Id", ondelete="RESTRICT"))
    Title = Column(String(100), unique=True, nullable=False)
    Amount = Column(Float, default=0)
    AmountOutstanding = Column(Float, default=0)
    ContractSigned = Column(Boolean, default=False)
    DateCreated = Column(TIMESTAMP, server_default=func.current_timestamp())

    Customer = relationship("Customer", backref="Contracts")
