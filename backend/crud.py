from sqlalchemy.orm import Session
import models, schemas

# --- PAZIENTE ---
# CREATE
def create_paziente(db: Session, paziente: schemas.PazienteCreate):
    db_paziente = models.Paziente(
        email = paziente.email,
        hashed_password = paziente.password,
        ruolo = models.RuoloUtente.paziente,

        nome = paziente.nome,
        cognome = paziente.cognome,
        sesso = paziente.sesso,
        codice_fiscale = paziente.codice_fiscale,
        indirizzo_residenza = paziente.indirizzo_residenza,
        indirizzo_domicilio = paziente.indirizzo_domicilio,
        recapito_telefonico = paziente.recapito_telefonico,
    )

    db.add(db_paziente)
    db.commit()
    db.refresh(db_paziente)
    return db_paziente

# READ
def get_paziente(db: Session, paziente_id: int):
    return db.query(models.Paziente).filter(models.Paziente.id_paziente == paziente_id).first()

def get_paziente_by_cf(db: Session, codice_fiscale: str):
    return db.query(models.Paziente).filter(models.Paziente.codice_fiscale == codice_fiscale).first()

def get_pazienti(db: Session, skip: int = 0, amount: int = 100):
    return db.query(models.Paziente).offset(skip).limit(amount).all()

# UPDATE

# DELETE

