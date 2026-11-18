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
def update_paziente(db: Session, paziente_id: int, dati_aggiornamento: schemas.PazienteUpdate):
    db_paziente = get_paziente(db, paziente_id)

    if db_paziente:
        # Trasforma i dati in ingresso in un dizionario, scartando i campi non inviati
        update_data = dati_aggiornamento.model_dump(exclude_unset=True)

        for chiave, valore in update_data.items():
            if chiave == "password":
                setattr(db_paziente, "hashed_password", valore)
            elif chiave == "ruolo":
                continue
            else:
                setattr(db_paziente, chiave, valore)

        db.commit()
        db.refresh(db_paziente)

    return db_paziente

# DELETE
def delete_paziente(db: Session, paziente_id: int):
    db_paziente = get_paziente(db, paziente_id)

    if db_paziente:
        db.delete(db_paziente)
        db.commit()

    return db_paziente