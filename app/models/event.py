from datetime import datetime

from sqlalchemy import TIMESTAMP, Column, Date, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship, validates

from app.models.contract import Contract
from app.models.employee import Employee

from .database import DatabaseConfig


class Event(DatabaseConfig.BASE):
    """
    Représente un événement dans la base de données.

    Attributes:
        Id (int): Identifiant unique de l'événement.
        ContractId (int): Identifiant du contrat associé à l'événement.
        EmployeeSupportId (int): Identifiant de l'employé support associé à l'événement.
        Title (str): Titre de l'événement.
        Notes (str): Notes supplémentaires sur l'événement.
        Location (str): Lieu de l'événement.
        Attendees (int): Nombre de participants à l'événement.
        DateStart (datetime.date): Date de début de l'événement.
        DateEnd (datetime.date): Date de fin de l'événement.
        DateCreated (datetime): Date de création de l'événement dans la base de données.
        Contract (Contract): Relation avec le contrat associé.
        EmployeeSupport (Employee): Relation avec l'employé support associé.
    """

    __tablename__ = "Event"

    Id = Column(Integer, primary_key=True)
    ContractId = Column(Integer, ForeignKey("Contract.Id", ondelete="CASCADE"), nullable=False)
    EmployeeSupportId = Column(Integer, ForeignKey("Employee.Id", ondelete="SET NULL"))
    Title = Column(String(100), nullable=False, unique=True)
    Notes = Column(Text)
    Location = Column(String(100))
    Attendees = Column(Integer)
    DateStart = Column(Date)
    DateEnd = Column(Date)
    DateCreated = Column(TIMESTAMP, server_default=func.current_timestamp())

    ContractRel = relationship("Contract", backref="EventsRel")
    EmployeeSupportRel = relationship("Employee", backref="EventsRel")

    @validates("DateStart", "DateEnd")
    def check_dates(self, key: str, value: str) -> str:
        """
        Valide les dates de début et de fin pour un événement.

        Args:
            key (str): Le nom de l'attribut (DateStart ou DateEnd).
            value (str): La valeur de la date sous forme de chaîne (format "dd-mm-yyyy").

        Returns:
            str: La valeur de la date validée.

        Raises:
            ValueError: Si le format de la date est invalide ou si la date de fin est avant la date de début.

        """
        if value:
            try:
                value = datetime.strptime(value, "%d-%m-%Y").date()
            except ValueError:
                raise ValueError("Format de date invalide. Utilisez le format dd-mm-yyyy")
            else:
                if key == "date_start":
                    self.date_start = value
                elif key == "date_end":
                    self.date_end = value

                if (key == "DateEnd" and self.DateStart and value and value <= self.DateStart) or (
                    key == "date_end" and self.date_start and value and value <= self.date_start
                ):
                    raise ValueError("La date de fin doit être après la date de début")

        return value

    @validates("Attendees")
    def check_attendees(self, key: str, value: any) -> int:
        """
        Valide l'attribut 'Attendees' d'une instance d'Event.

        Cette méthode s'assure que la valeur assignée à 'Attendees' est un entier valide et positif.
        Elle effectue les vérifications suivantes :
        1. Convertit la valeur en entier.
        2. Vérifie que la valeur est non négative.

        Args:
            key (str): Le nom de l'attribut en cours de validation.
            value: La valeur assignée à l'attribut 'Attendees'.

        Returns:
            int: La valeur validée pour 'Attendees'.

        Raises:
            ValueError: Si la valeur n'est pas un entier valide ou si elle est négative.
        """

        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError(f"{key} doit être un nombre valide.")

        if value < 0:
            raise ValueError(f"{key} doit être positif.")

        return value
