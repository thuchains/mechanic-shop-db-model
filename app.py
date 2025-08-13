from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Date, Float, Integer, ForeignKey
from datetime import date

app = Flask(__name__) 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db' #connecting a sqlite db to our flask app

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class = Base)

db.init_app(app)

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
    password: Mapped[str] = mapped_column(String(150), nullable=False, unique=False)
    salary: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)

    ticket_mechanics: Mapped[list['Ticket_mechanics']] = relationship('Ticket_mechanics', back_populates='mechanics')

class Service_tickets(Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey('customers.id'), nullable=False)
    service_desc: Mapped[str] = mapped_column(String(500), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    vin: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    service_date: Mapped[date] = mapped_column(Date, nullable=False)

    customer: Mapped['Customers'] = relationship('Customers')
    ticket_mechanics: Mapped[list['Ticket_mechanics']] = relationship('Ticket_mechanics', back_populates='service_ticket')

class Ticket_mechanics(Base):
    __tablename__ = 'ticket_mechanics'

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey('service_tickets.id'), nullable=False)
    mechanic_id: Mapped[int] = mapped_column(Integer, ForeignKey('mechanics.id'), nullable=False)

    service_ticket: Mapped['Service_tickets'] = relationship('Service_tickets', back_populates='ticket_mechanics')
    mechanics: Mapped['Mechanics'] = relationship('Mechanics', back_populates='ticket_mechanics')




with app.app_context():
    db.create_all() 