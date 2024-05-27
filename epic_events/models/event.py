from sqlalchemy import TIMESTAMP, Column, Date, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship, validates
from datetime import datetime

from epic_events.models.contract import Contract
from epic_events.models.employee import Employee

from .database import Base


class Event(Base):
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
    ContractId = Column(Integer, ForeignKey("Contract.Id"))
    EmployeeSupportId = Column(Integer, ForeignKey("Employee.Id"))
    Title = Column(String(100), nullable=False, unique=True)
    Notes = Column(Text)
    Location = Column(String(100))
    Attendees = Column(Integer)
    DateStart = Column(Date)
    DateEnd = Column(Date)
    DateCreated = Column(TIMESTAMP, server_default=func.current_timestamp())

    ContractRel = relationship("Contract", backref="EventsRel")
    EmployeeSupportRel = relationship("Employee", backref="EventsRel")

    # Valider la date de fin après la date de début et le format de date
    @validates("DateStart", "DateEnd")
    def check_dates(self, key, value):
        if value:
            try:
                datetime.strptime(value, "%d-%m-%Y")
            except ValueError:
                raise ValueError("Format de date invalide. Utilisez le format dd-mm-yyyy")
        if key == "DateEnd" and self.DateStart and value and value <= self.DateStart:
            raise ValueError("La date de fin doit être après la date de début")
        
        return value
    
        
