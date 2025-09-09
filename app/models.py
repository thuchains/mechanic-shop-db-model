from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Integer, ForeignKey, DateTime, Table, Column
from datetime import datetime




class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class = Base) #Only extension that we are instantiating outside of extensions file

ticket_mechanics = Table(
    "ticket_mechanics", 
    Base.metadata,
    Column("service_ticket_id", Integer, ForeignKey("service_tickets.id"), primary_key=True),
    Column("mechanic_id", Integer, ForeignKey("mechanics.id"), primary_key=True)
)

# ticket_parts = Table(
#     "ticket_parts", 
#     Base.metadata, 
#     Column("service_ticket_id", Integer, ForeignKey("service_tickets.id"), primary_key=True),
#     Column("part_id", Integer, ForeignKey("parts.id"), primary_key=True) 
#     )


class Customers(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(15), nullable=False, unique=True)
    address: Mapped[str] = mapped_column(String(200), nullable=False)

class Mechanics(Base):
    __tablename__ = 'mechanics'

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(500), nullable=False, unique=False)
    salary: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)

    service_tickets: Mapped[list['ServiceTickets']] = relationship("ServiceTickets", secondary=ticket_mechanics, back_populates="mechanics")

class ServiceTickets(Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey('customers.id'), nullable=False)
    service_desc: Mapped[str] = mapped_column(String(500), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    vin: Mapped[str] = mapped_column(String(200), nullable=False)
    service_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    
    mechanics: Mapped[list['Mechanics']] = relationship("Mechanics", secondary=ticket_mechanics, back_populates="service_tickets")
    customer: Mapped['Customers'] = relationship('Customers')
    parts: Mapped[list['Parts']] = relationship("Parts", back_populates="service_ticket")
    
class PartDescriptions(Base):
    __tablename__ = 'part_descriptions'

    id: Mapped[int] = mapped_column(primary_key=True)
    part_name: Mapped[str] = mapped_column(String(150), nullable=False)
    price: Mapped[float] = mapped_column(Float)

    parts: Mapped[list['Parts']] = relationship("Parts", back_populates="part_description")

class Parts(Base):
    __tablename__ = 'parts'

    id: Mapped[int] = mapped_column(primary_key=True)
    desc_id: Mapped[int] = mapped_column(Integer, ForeignKey('part_descriptions.id'), nullable=False)
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey('service_tickets.id'), nullable=True)

    part_description: Mapped['PartDescriptions'] = relationship("PartDescriptions", back_populates="parts")
    service_ticket: Mapped['ServiceTickets'] = relationship("ServiceTickets", back_populates="parts")

    