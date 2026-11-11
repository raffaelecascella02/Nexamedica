from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from datetime import date
import codicefiscale
from models import RuoloUtente, Sesso, MansioneAmministratore, StatoPagamento, StatoVisita # Importiamo gli Enum di SQLAlchemy da models.py

# --- ACCOUNT ---
class AccountBase(BaseModel):
    email: EmailStr
    ruolo: RuoloUtente

class AccountCreate(AccountBase):
    password: str

class AccountResponse(AccountBase):
    id_account: int
    model_config = ConfigDict(from_attributes=True)

# --- PAZIENTE ---
class PazienteBase(AccountBase):
    nome: str
    cognome: str
    sesso: Sesso
    codice_fiscale: str = Field(..., pattern=r"^[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]$")
    indirizzo_residenza: str
    indirizzo_domicilio: str
    recapito_telefonico: str

    # check sulla validità del codice fiscale attraverso la libreria apposita
    @field_validator("codice_fiscale")
    @classmethod
    def valida_cin(cls, v: str) -> str:
        # La libreria verifica il checksum (sostanza)
        if not codicefiscale.isvalid(v):
            raise ValueError("Il codice fiscale non è valido: carattere di controllo errato")
        return v

class PazienteCreate(PazienteBase):
    password: str

class PazienteResponse(PazienteBase):
    id_paziente: int
    model_config = ConfigDict(from_attributes=True)

# --- MEDICO ---
class MedicoBase(AccountBase):
    nome: str
    cognome: str
    matricola: str = Field(..., min_length=5, max_length=10)
    specializzazione: str
    reparto: str

class MedicoCreate(MedicoBase):
    password: str

class MedicoResponse(MedicoBase):
    id_medico: int
    model_config = ConfigDict(from_attributes=True)

# --- AMMINISTRATORE ---
class AmministratoreBase(AccountBase):
    nome: str
    cognome: str
    mansione: MansioneAmministratore

class AmministratoreCreate(AmministratoreBase):
    password: str

class AmministratoreResponse(AmministratoreBase):
    id_amministratore: int
    model_config = ConfigDict(from_attributes=True)

# --- CATALOGO PRESTAZIONI ---
class CatalogoPrestazioniBase(BaseModel):
    nome_visita: str
    costo_base: float

class CatalogoPrestazioniCreate(CatalogoPrestazioniBase):
    pass

class CatalogoPrestazioniResponse(CatalogoPrestazioniBase):
    id_prestazione: int
    model_config = ConfigDict(from_attributes=True)

# --- PRENOTAZIONE ---
class PrenotazioneBase(BaseModel):
    id_paziente: int
    id_medico: int
    id_prestazione: int
    data_prenotazione: date
    data_appuntamento: date
    luogo: str
    stato_visita: StatoVisita
    costo_applicato: float
    stato_pagamento: StatoPagamento

class PrenotazioneCreate(PrenotazioneBase):
    pass

class PrenotazioneResponse(PrenotazioneBase):
    id_prenotazione: int
    model_config = ConfigDict(from_attributes=True)

# --- REFERTO ---
class RefertoBase(BaseModel):
    id_prenotazione: int
    data_emissione: date
    descrizione_sintomi: str | None = None
    diagnosi: str

class RefertoCreate(RefertoBase):
    pass

class RefertoResponse(RefertoBase):
    id_referto: int
    model_config = ConfigDict(from_attributes=True)