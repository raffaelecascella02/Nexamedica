from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, get_db
import models, crud, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nexamedica API")

# Rotta di test base per verificare che il server risponda
@app.get("/")
def read_root():
    return {"stato": "Online", "messaggio": "Database Nexamedica inizializzato con successo!"}

#region PAZIENTE
# Rotta per leggere tutti i pazienti inseriti
@app.get("/pazienti/", response_model=list[schemas.PazienteResponse])
def lista_pazienti(db: Session=Depends(get_db)):
    return crud.get_pazienti(db)

# Rotta per l'inserimento di un paziente a DB
@app.post("/pazienti/", response_model=schemas.PazienteResponse)
def create_paziente(paziente: schemas.PazienteCreate, db: Session=Depends(get_db)):
    db_paziente = crud.get_paziente_by_cf(db, codice_fiscale=paziente.codice_fiscale)

    if db_paziente:
        raise HTTPException(status_code=400, detail="Codice Fiscale già registrato a sistema.")
    
    return crud.create_paziente(db=db, paziente=paziente)

# Rotta per l'aggiornamento di un paziente (payload parziale)
@app.patch("/pazienti/{id_paziente}", response_model=schemas.PazienteResponse)
def update_paziente(id_paziente: int, aggiornamento_paziente: schemas.PazienteUpdate, db: Session = Depends(get_db)):
    db_paziente = crud.get_paziente(db, paziente_id=id_paziente)

    if not db_paziente:
        raise HTTPException(status_code=404, detail="ID paziente non presente a sistema.")

    return crud.update_paziente(db=db, paziente_id=id_paziente, dati_aggiornamento=aggiornamento_paziente)

# Rotta per l'eliminazione di un paziente a DB tramite ID (PK)
@app.delete("/pazienti/{id_paziente}", response_model=schemas.PazienteResponse)
def delete_paziente(id_paziente: int, db: Session=Depends(get_db)):
    db_paziente = crud.delete_paziente(db, id_paziente)

    if not db_paziente:
        raise HTTPException(status_code=404, detail="ID paziente non presente a sistema.")

    return db_paziente

# Rotta per l'eliminazione di un paziente a DB tramite Codice Fiscale
@app.delete("/pazienti/cf/{codice_fiscale}", response_model=schemas.PazienteResponse)
def delete_paziente_by_cf(codice_fiscale: str, db: Session = Depends(get_db)):
    db_paziente = crud.delete_paziente_by_cf(db, codice_fiscale)

    if not db_paziente:
        raise HTTPException(status_code=404, detail="Codice Fiscale paziente non presente a sistema.")

    return db_paziente
#endregion

#region MEDICO
# Rotta per leggere tutti i medici inseriti
@app.get("/medici/", response_model=list[schemas.MedicoResponse])
def lista_medici(db: Session=Depends(get_db)):
    return crud.get_medici(db)

# Rotta per l'inserimento di un medico a DB
@app.post("/medici/", response_model=schemas.MedicoResponse)
def create_medico(medico: schemas.MedicoCreate, db: Session=Depends(get_db)):
    db_medico = crud.get_medico_by_matricola(db, matricola=medico.matricola)

    if db_medico:
        raise HTTPException(status_code=400, detail="Matricola già registrata a sistema.")
    
    return crud.create_medico(db=db, medico=medico)

# Rotta per l'aggiornamento di un medico (payload parziale)
@app.patch("/medici/{id_medico}", response_model=schemas.MedicoResponse)
def update_medico(id_medico: int, aggiornamento_medico: schemas.MedicoUpdate, db: Session = Depends(get_db)):
    db_medico = crud.get_medico(db, medico_id=id_medico)

    if not db_medico:
        raise HTTPException(status_code=404, detail="ID medico non presente a sistema.")

    return crud.update_medico(db=db, medico_id=id_medico, dati_aggiornamento=aggiornamento_medico)

# Rotta per l'eliminazione di un medico a DB tramite ID (PK)
@app.delete("/medici/{id_medico}", response_model=schemas.MedicoResponse)
def delete_medico(id_medico: int, db: Session=Depends(get_db)):
    db_medico = crud.delete_medico(db, id_medico)

    if not db_medico:
        raise HTTPException(status_code=404, detail="ID medico non presente a sistema.")

    return db_medico

# Rotta per l'eliminazione di un medico a DB tramite matricola
@app.delete("/medici/matricola/{matricola}", response_model=schemas.MedicoResponse)
def delete_medico_by_matricola(matricola: str, db: Session = Depends(get_db)):
    db_medico = crud.delete_medico_by_matricola(db, matricola)

    if not db_medico:
        raise HTTPException(status_code=404, detail="Matricola medico non presente a sistema.")

    return db_medico
#endregion

