from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String, func, select

from .database import Base


class Role(Base):
    """
    Représente un rôle dans la base de données.

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
    Can_ru_Customer = Column(Boolean, nullable=False, default=False)
    Can_crud_Customer = Column(Boolean, nullable=False, default=False)
    Can_access_all_Customer = Column(Boolean, nullable=False, default=False)
    Can_ru_Contract = Column(Boolean, nullable=False, default=False)
    Can_crud_Contract = Column(Boolean, nullable=False, default=False)
    Can_access_all_Contract = Column(Boolean, nullable=False, default=False)
    Can_ru_Event = Column(Boolean, nullable=False, default=False)
    Can_crud_Event = Column(Boolean, nullable=False, default=False)
    Can_access_all_Event = Column(Boolean, nullable=False, default=False)
    Can_access_support_Event = Column(Boolean, nullable=False, default=False)
    DateCreated = Column(TIMESTAMP, server_default=func.current_timestamp())

    @classmethod
    def get_roles_list(cls, session):
        """
        Retourne une liste des rôles avec leur ID et leur nom.

        Args:
            session: Session SQLAlchemy active.

        Returns:
            list: Liste de tuples contenant l'ID et le nom de chaque rôle.
        """
        roles = session.query(cls.Id, cls.RoleName).all()
        return roles
