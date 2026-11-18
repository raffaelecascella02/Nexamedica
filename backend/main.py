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

# Rotta per leggere tutti i pazienti inseriti
@app.get("/pazienti")
def lista_pazienti(db: Session=Depends(get_db)):
    return crud.get_pazienti(db)


# Rotta per l'inserimento di un paziente a DB
@app.post("/pazienti/", response_model=schemas.PazienteResponse)
def create_paziente(paziente: schemas.PazienteCreate, db: Session=Depends(get_db)):
    db_paziente = crud.get_paziente_by_cf(db, codice_fiscale=paziente.codice_fiscale)

    if db_paziente:
        raise HTTPException(status_code=400, detail="Codice Fiscale già registrato a sistema.")
    
    return crud.create_paziente(db=db, paziente=paziente)

# Rotta per l'eliminazione di un paziente a DB tramite ID (PK)
@app.delete("/pazienti/{id_paziente}", response_model=schemas.PazienteResponse)
def delete_paziente(id_paziente: int, db: Session=Depends(get_db)):
    db_paziente = crud.get_paziente(db, id_paziente)

    if not db_paziente:
        raise HTTPException(status_code=404, detail="ID paziente non presente a sistema.")

    return crud.delete_paziente(db=db, paziente_id=id_paziente)

# Rotta per l'aggiornamento di un paziente (payload parziale)
@app.patch("/pazienti/{id_paziente}", response_model=schemas.PazienteResponse)
def update_paziente(id_paziente: int, aggiornamento_paziente: schemas.PazienteUpdate, db: Session = Depends(get_db)):
    db_paziente = crud.get_paziente(db, paziente_id=id_paziente)

    if not db_paziente:
        raise HTTPException(status_code=404, detail="ID paziente non presente a sistema.")

    return crud.update_paziente(db=db, paziente_id=id_paziente, dati_aggiornamento=aggiornamento_paziente)

