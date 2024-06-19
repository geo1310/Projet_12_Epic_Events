from sqlalchemy import TIMESTAMP, Boolean, Column, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship, validates

from app.models.customer import Customer

from .database import DatabaseConfig


class Contract(DatabaseConfig.BASE):
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
    CustomerId = Column(Integer, ForeignKey("Customer.Id", ondelete="SET NULL"))
    Title = Column(String(100), unique=True, nullable=False)
    Amount = Column(Float, default=0)
    AmountOutstanding = Column(Float, default=0)
    ContractSigned = Column(Boolean, default=False)
    DateCreated = Column(TIMESTAMP, server_default=func.current_timestamp())

    CustomerRel = relationship("Customer", backref="ContractsRel")

    @validates("Amount", "AmountOutstanding")
    def validate_amount(self, key, value):
        """
        Valide que les montants (Amount et AmountOutstanding) sont des floats positifs et que AmountOutstanding
        n'est pas supérieur à Amount.

        Args:
            key (str): Le nom du champ à valider.
            value (float): La valeur du montant à valider.

        Returns:
            float: La valeur validée du montant.

        Raises:
            ValueError: Si le montant n'est pas un float, s'il est négatif ou si AmountOutstanding est supérieur à Amount.
        """

        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{key} doit être un nombre valide.")

        if value < 0:
            raise ValueError(f"{key} doit être positif.")

        if key == "amount":
            self._amount = value
        elif key == "amount_outstanding":
            self._amount_outstanding = value
            if hasattr(self, "_amount") and value > self._amount:
                raise ValueError("AmountOutstanding ne peut pas être supérieur à Amount.")

        return value
