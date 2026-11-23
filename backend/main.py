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

# Rotta per leggere i dati di un paziente da DB
@app.get("/pazienti/{id_paziente}", response_model=schemas.PazienteResponse)
def lista_paziente_by_id(id_paziente: int, db: Session = Depends(get_db)):
    db_paziente = crud.get_paziente(db, id_paziente)

    if not db_paziente:
        raise HTTPException(status_code=404, detail="ID paziente non presente a sistema.")

    return db_paziente

# Rotta per l'inserimento di un paziente a DB
@app.post("/pazienti/", response_model=schemas.PazienteResponse, status_code=201)
def create_paziente(paziente: schemas.PazienteCreate, db: Session=Depends(get_db)):
    db_paziente = crud.get_paziente_by_cf(db, codice_fiscale=paziente.codice_fiscale)

    if db_paziente:
        raise HTTPException(status_code=400, detail="Codice Fiscale già registrato a sistema.")
    
    return crud.create_paziente(db, paziente)

# Rotta per l'aggiornamento di un paziente (payload parziale)
@app.patch("/pazienti/{id_paziente}", response_model=schemas.PazienteResponse)
def update_paziente(id_paziente: int, aggiornamento_paziente: schemas.PazienteUpdate, db: Session = Depends(get_db)):
    db_paziente = crud.get_paziente(db, id_paziente)

    if not db_paziente:
        raise HTTPException(status_code=404, detail="ID paziente non presente a sistema.")

    return crud.update_paziente(db, id_paziente, aggiornamento_paziente)

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

# Rotta per leggere i dati di un medico da DB
@app.get("/medici/{id_medico}", response_model=schemas.MedicoResponse)
def lista_medico_by_id(id_medico: int, db: Session = Depends(get_db)):
    db_medico = crud.get_medico(db, id_medico)

    if not db_medico:
            raise HTTPException(status_code=404, detail="ID medico non presente a sistema.")
    
    return db_medico

# Rotta per l'inserimento di un medico a DB
@app.post("/medici/", response_model=schemas.MedicoResponse, status_code=201)
def create_medico(medico: schemas.MedicoCreate, db: Session=Depends(get_db)):
    db_medico = crud.get_medico_by_matricola(db, matricola=medico.matricola)

    if db_medico:
        raise HTTPException(status_code=400, detail="Matricola già registrata a sistema.")
    
    return crud.create_medico(db, medico)

# Rotta per l'aggiornamento di un medico (payload parziale)
@app.patch("/medici/{id_medico}", response_model=schemas.MedicoResponse)
def update_medico(id_medico: int, aggiornamento_medico: schemas.MedicoUpdate, db: Session = Depends(get_db)):
    db_medico = crud.get_medico(db, id_medico)

    if not db_medico:
        raise HTTPException(status_code=404, detail="ID medico non presente a sistema.")

    return crud.update_medico(db, id_medico, aggiornamento_medico)

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

#region CATALOGO PRESTAZIONI
# Rotta per leggere tutte le prestazioni presenti nel catalogo
@app.get("/prestazioni/", response_model=list[schemas.CatalogoPrestazioniResponse])
def lista_prestazioni(db: Session = Depends(get_db)):
    db_prestazione = crud.get_prestazioni(db)
    return db_prestazione

# Rotta per leggere i dati di una prestazione presente nel catalogo
@app.get("/prestazioni/{id_prestazione}", response_model=schemas.CatalogoPrestazioniResponse)
def lista_prestazione_by_id(id_prestazione: int, db: Session = Depends(get_db)):
    db_prestazione = crud.get_prestazione(db, id_prestazione)

    if not db_prestazione:
            raise HTTPException(status_code=404, detail="ID prestazione non presente a sistema.")
    
    return db_prestazione   

# Rotta per inserire una nuova prestazione nel catalogo
@app.post("/prestazioni/", response_model=schemas.CatalogoPrestazioniResponse, status_code=201)
def create_prestazione(prestazione: schemas.CatalogoPrestazioniCreate, db: Session = Depends(get_db)):
    db_prestazione = crud.get_prestazione_by_nome(db, nome_visita=prestazione.nome_visita)

    if db_prestazione:
        raise HTTPException(status_code=400, detail="Prestazione già presente a catalogo.")

    return crud.create_prestazione(db, prestazione)

# Rotta per modificare una prestazione
@app.patch("/prestazioni/{id_prestazione}", response_model=schemas.CatalogoPrestazioniResponse)
def update_prestazione(id_prestazione: int, dati_aggiornamento: schemas.CatalogoPrestazioniUpdate, db: Session = Depends(get_db)):
    db_prestazione = crud.get_prestazione(db, id_prestazione)

    if not db_prestazione:
        raise HTTPException(status_code=404, detail="ID prestazione non presente a catalogo.")
    
    return crud.update_prestazione(db, id_prestazione, dati_aggiornamento)

# Rotta per cancellare una prestazione presente nel catalogo
@app.delete("/prestazioni/{id_prestazione}")
def delete_prestazione(id_prestazione: int, db: Session = Depends(get_db)):
    db_prestazione = crud.delete_prestazione(db, id_prestazione)

    if not db_prestazione:
        raise HTTPException(status_code=404, detail="ID prestazione non presente a catalogo.")

    return db_prestazione
#endregion