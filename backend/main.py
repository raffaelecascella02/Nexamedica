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


# Rotta per l'inserimento di un paziente a DB
@app.post("/pazienti/", response_model=schemas.PazienteResponse)
def create_paziente(paziente: schemas.PazienteCreate, db: Session = Depends(get_db)):
    db_paziente = crud.get_paziente_by_cf(db, codice_fiscale=paziente.codice_fiscale)

    if db_paziente:
        raise HTTPException(status_code=400, detail="Codice Fiscale già registrato a sistema.")
    
    return crud.create_paziente(db=db, paziente=paziente)
