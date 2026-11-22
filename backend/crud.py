from sqlalchemy.orm import Session
import models, schemas, security

#region PAZIENTE
# CREATE
def create_paziente(db: Session, paziente: schemas.PazienteCreate):
    db_paziente = models.Paziente(
        email = paziente.email,
        hashed_password = security.get_password_hash(paziente.password),
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
                setattr(db_paziente, "hashed_password", security.get_password_hash(valore))
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

def delete_paziente_by_cf(db: Session, codice_fiscale: str):
    db_paziente = get_paziente_by_cf(db, codice_fiscale.upper())
    if db_paziente:
        db.delete(db_paziente)
        db.commit()
    return db_paziente

#endregion

#region MEDICO
# CREATE
def create_medico(db: Session, medico: schemas.MedicoCreate):
    db_medico = models.Medico(
        email = medico.email,
        hashed_password = security.get_password_hash(medico.password),
        ruolo = models.RuoloUtente.medico,

        nome = medico.nome,
        cognome = medico.cognome,
        matricola = medico.matricola.upper(),
        specializzazione = medico.specializzazione,
        reparto = medico.reparto
    )

    db.add(db_medico)
    db.commit()
    db.refresh(db_medico)
    return db_medico

# READ
def get_medico(db: Session, medico_id: int):
    return db.query(models.Medico).filter(models.Medico.id_medico == medico_id).first()

def get_medico_by_matricola(db: Session, matricola: str):
    return db.query(models.Medico).filter(models.Medico.matricola == matricola).first()

def get_medici(db: Session, skip: int = 0, amount: int = 100):
    return db.query(models.Medico).offset(skip).limit(amount).all()

# UPDATE
def update_medico(db: Session, medico_id: int, dati_aggiornamento: schemas.MedicoUpdate):
    db_medico = get_medico(db, medico_id)

    if db_medico:
        update_data = dati_aggiornamento.model_dump(exclude_unset=True)
    
        for chiave, valore in update_data.items():
            if chiave == "password":
                setattr(db_medico, "hashed_password", security.get_password_hash(valore))
            elif chiave == "ruolo":
                continue
            else:
                setattr(db_medico, chiave, valore)

        db.commit()
        db.refresh(db_medico)

    return db_medico

# DELETE
def delete_medico(db: Session, medico_id: int):
    db_medico = get_medico(db, medico_id)

    if db_medico:
        db.delete(db_medico)
        db.commit()

    return db_medico

def delete_medico_by_matricola(db: Session, matricola: str):
    db_medico = get_medico_by_matricola(db, matricola.upper())
    if db_medico:
        db.delete(db_medico)
        db.commit()
    return db_medico
#endregion
