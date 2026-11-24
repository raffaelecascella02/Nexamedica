from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from typing import Optional
from datetime import date
import codicefiscale
from models import RuoloUtente, Sesso, MansioneAmministratore, StatoPagamento, StatoVisita # Importiamo gli Enum di SQLAlchemy da models.py

#region ACCOUNT
class AccountBase(BaseModel):
    email: EmailStr
    ruolo: RuoloUtente

class AccountCreate(AccountBase):
    password: str

class AccountResponse(AccountBase):
    id_account: int
    model_config = ConfigDict(from_attributes=True)
#endregion

#region PAZIENTE
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

# Schema per l'aggiornamento parziale (PATCH/PUT) - Tutti i campi sono opzionali
class PazienteUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nome: Optional[str] = None
    cognome: Optional[str] = None
    sesso: Optional[Sesso] = None
    codice_fiscale: Optional[str] = Field(None, pattern=r"^[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]$")
    indirizzo_residenza: Optional[str] = None
    indirizzo_domicilio: Optional[str] = None
    recapito_telefonico: Optional[str] = None
    password: Optional[str] = None
#endregion

#region MEDICO
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

class MedicoUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nome: Optional[str] = None
    cognome: Optional[str] = None
    matricola: Optional[str] = Field(None, min_length=5, max_length=10)
    specializzazione: Optional[str] = None
    reparto: Optional[str] = None
    password: Optional[str] = None
#endregion

#region AMMINISTRATORE
class AmministratoreBase(AccountBase):
    nome: str
    cognome: str
    mansione: MansioneAmministratore

class AmministratoreCreate(AmministratoreBase):
    password: str

class AmministratoreResponse(AmministratoreBase):
    id_amministratore: int
    model_config = ConfigDict(from_attributes=True)
#endregion

#region CATALOGO PRESTAZIONI
class CatalogoPrestazioniBase(BaseModel):
    nome_visita: str
    costo_base: float = Field(..., gt=0)

class CatalogoPrestazioniCreate(CatalogoPrestazioniBase):
    pass

class CatalogoPrestazioniResponse(CatalogoPrestazioniBase):
    id_prestazione: int
    model_config = ConfigDict(from_attributes=True)

class CatalogoPrestazioniUpdate(BaseModel):
    nome_visita: Optional[str] = None
    costo_base: Optional[float] = Field(None, gt=0)
#endregion

#region PRENOTAZIONE
class PrenotazioneBase(BaseModel):
    id_paziente: int = Field(..., gt=0)
    id_medico: int = Field(..., gt=0)
    id_prestazione: int = Field(..., gt=0)
    data_prenotazione: date
    data_appuntamento: date
    luogo: str
    stato_visita: StatoVisita
    stato_pagamento: StatoPagamento

class PrenotazioneCreate(PrenotazioneBase):
    pass

class PrenotazioneResponse(PrenotazioneBase):
    id_prenotazione: int
    model_config = ConfigDict(from_attributes=True)
    costo_applicato: float = Field(..., ge=0)

class PrenotazioneUpdate(BaseModel):
    data_appuntamento: Optional[date] = None
    luogo: Optional[str] = None
    stato_visita: Optional[StatoVisita] = None
    costo_applicato: Optional[float] = Field(None, ge=0)
    stato_pagamento: Optional[StatoPagamento] = None
#endregion

#region REFERTO
class RefertoBase(BaseModel):
    id_prenotazione: int = Field(..., gt=0)
    data_emissione: date
    descrizione_sintomi: str | None = None
    diagnosi: str = Field(..., min_length=1)

class RefertoCreate(RefertoBase):
    pass

class RefertoResponse(RefertoBase):
    id_referto: int
    model_config = ConfigDict(from_attributes=True)

class RefertoUpdate(BaseModel):
    data_emissione: Optional[date] = None
    descrizione_sintomi: Optional[str] = None
    diagnosi: Optional[str] = Field(None, min_length=1)
#endregion