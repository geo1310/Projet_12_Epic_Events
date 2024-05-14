from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    Enum,
    TIMESTAMP,
    Date,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship, declarative_base, validates
from passlib.hash import bcrypt

Base = declarative_base()  # classe de base pour tous les modèles


class Employee(Base):
    __tablename__ = "Employee"

    Id = Column(Integer, primary_key=True, autoincrement=True)  # mettre index=True sur les champs ???
    FirstName = Column(String(100))
    LastName = Column(String(100))
    Email = Column(String(100), unique=True, nullable=False)
    PasswordHash = Column(String(100), nullable=False)
    RoleId = Column(Integer, ForeignKey("Role.Id", ondelete="RESTRICT"))
    DateCreated = Column(TIMESTAMP, server_default=func.current_timestamp())

    Role = relationship("Role", backref="Employees")

    @validates("password_hash")
    def validate_password_hash(self, key, password):
        return bcrypt.hash(password)


class Role(Base):
    __tablename__ = "Role"

    Id = Column(Integer, primary_key=True)
    RoleName = Column(String(100), nullable=False, unique=True)
    Can_r_Employee = Column(Boolean, nullable=False, default=False)
    Can_ru_Employee = Column(Boolean, nullable=False, default=False)
    Can_crud_Employee = Column(Boolean, nullable=False, default=False)
    Can_r_role = Column(Boolean, nullable=False, default=False)
    Can_ru_role = Column(Boolean, nullable=False, default=False)
    Can_crud_role = Column(Boolean, nullable=False, default=False)
    Can_r_Customer = Column(Boolean, nullable=False, default=False)
    Can_ru_customer = Column(Boolean, nullable=False, default=False)
    Can_crud_Customer = Column(Boolean, nullable=False, default=False)
    Can_r_Contract = Column(Boolean, nullable=False, default=False)
    Can_ru_Contract = Column(Boolean, nullable=False, default=False)
    Can_crud_Contract = Column(Boolean, nullable=False, default=False)
    Can_r_Event = Column(Boolean, nullable=False, default=False)
    Can_ru_Event = Column(Boolean, nullable=False, default=False)
    Can_crud_Event = Column(Boolean, nullable=False, default=False)
    DateCreated = Column(TIMESTAMP, server_default=func.current_timestamp())


class Customer(Base):
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


class Contract(Base):
    __tablename__ = "Contract"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    CustomerId = Column(Integer, ForeignKey("Customer.Id", ondelete="RESTRICT"))
    Title = Column(String(100), unique=True, nullable=False)
    Amount = Column(Float, default=0)
    AmountOutstanding = Column(Float, default=0)
    ContractSigned = Column(Boolean, default=False)
    DateCreated = Column(TIMESTAMP, server_default=func.current_timestamp())

    Customer = relationship("Customer", backref="Contracts")


class Event(Base):
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

    Contract = relationship("Contract", backref="Events")
    EmployeeSupport = relationship("Employee", backref="Events")
