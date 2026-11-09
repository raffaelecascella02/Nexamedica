from sqlalchemy import Column, ForeignKey, Integer, String, Float, Date, Enum
from database import Base
import enum

# Definizione degli Enum per limitare le selezioni
class RuoloUtente(str, enum.Enum):
    admin = "admin"
    medico = "medico"
    paziente = "paziente"

class Sesso(str, enum.Enum):
    M = "M"
    F = "F"
    altro = "Altro"

class StatoVisita(str, enum.Enum):
    programmata = "Programmata"
    completata = "Completata"
    cancellata = "Cancellata"

class StatoPagamento(str, enum.Enum):
    da_saldare = "Da saldare"
    saldato = "Saldato"

class MansioneAmministratore(str, enum.Enum):
    segreteria = "Segreteria"
    direzione = "Direzione"
    it_sysadmin = "IT System Administrator"

# Definizione delle classi ORM
class Account(Base):
    __tablename__ = "account"

    id_account = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    ruolo = Column(Enum(RuoloUtente), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "account",
        "polymorphic_on": ruolo,
    }

class Amministratore(Account):
    __tablename__ = "amministratore"

    id_amministratore = Column(Integer, ForeignKey("account.id_account"), primary_key=True)
    nome = Column(String, nullable=False)
    cognome = Column(String, nullable=False)
    mansione = Column(Enum(MansioneAmministratore), nullable=False, default=MansioneAmministratore.segreteria)

    __mapper_args__ = {
        "polymorphic_identity": "amministratore",
    }

class Paziente(Account):
    __tablename__ = "paziente"

    id_paziente = Column(Integer, ForeignKey("account.id_account"), primary_key=True)
    nome = Column(String, nullable=False)
    cognome = Column(String, nullable=False)
    sesso = Column(Enum(Sesso), nullable=False)
    codice_fiscale = Column(String, nullable=False)
    indirizzo_residenza = Column(String, nullable=False)
    indirizzo_domicilio = Column(String, nullable=False)
    recapito_telefonico = Column(String, nullable = False)

    __mapper_args__ = {
        "polymorphic_identity": "paziente",
    }

class Medico(Account):
    __tablename__ = "medico"

    id_medico = Column(Integer, ForeignKey("account.id_account"), primary_key=True)
    nome = Column(String, nullable=False)
    cognome = Column(String, nullable=False)
    matricola = Column(String, nullable=False, index=True)
    specializzazione = Column(String, nullable=False, index=True)
    reparto = Column(String, nullable=False, index=True)

    __mapper_args__ = {
        "polymorphic_identity": "medico",
    }

class CatalogoPrestazioni(Base):
    __tablename__ = "catalogo_prestazioni"

    id_prestazione = Column(Integer, primary_key=True)
    nome_visita = Column(String, nullable=False, index=True)
    costo_base = Column(Float, nullable=False)

class Prenotazione(Base):
    __tablename__ = "prenotazione"

    id_prenotazione = Column(Integer, primary_key=True)
    id_paziente = Column(Integer, ForeignKey("paziente.id_paziente"))
    id_medico = Column(Integer, ForeignKey("medico.id_medico"))
    id_prestazione = Column(Integer, ForeignKey("catalogo_prestazioni.id_prestazione"))
    data_prenotazione = Column(Date, nullable=False)
    data_appuntamento = Column(Date, nullable=False)
    luogo = Column(String, nullable=False)
    stato_visita = Column(Enum(StatoVisita), nullable=False)
    costo_applicato = Column(Float, nullable=False)
    stato_pagamento = Column(Enum(StatoPagamento), nullable=False)

class Referto(Base):
    __tablename__ = "referto"

    id_referto = Column(Integer, primary_key=True)
    id_prenotazione = Column(Integer, ForeignKey("prenotazione.id_prenotazione"))
    data_emissione = Column(Date, nullable=False)
    descrizione_sintomi = Column(String)
    diagnosi = Column(String, nullable=False)