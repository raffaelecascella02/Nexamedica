from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db
import models, crud, schemas, security
from typing import cast
from datetime import date

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nexamedica API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotta di test base per verificare che il server risponda
@app.get("/")
def read_root():
    return {"stato": "Online", "messaggio": "Database Nexamedica inizializzato con successo!"}

#region AUTENTICAZIONE
# Rotta di login OAuth2: verifica email/password e restituisce il token JWT
@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm usa il campo 'username': nel nostro caso contiene l'email
    db_account = crud.get_account_by_email(db, form_data.username)

    if not db_account or not security.verify_password(form_data.password, cast(str, db_account.hashed_password)):
        raise HTTPException(
            status_code=401,
            detail="Email o password non corretti.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = security.create_access_token(
        data={"sub": str(db_account.id_account), "ruolo": db_account.ruolo.value}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Rotta protetta per verificare il token e leggere i dati dell'utente autenticato
@app.get("/me", response_model=schemas.AccountResponse)
def read_me(current_user: models.Account = Depends(security.get_current_user)):
    return current_user
#endregion

#region PAZIENTE
# Rotta per leggere tutti i pazienti inseriti
@app.get("/pazienti/", response_model=list[schemas.PazienteResponse])
def lista_pazienti(db: Session=Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.admin, models.RuoloUtente.medico))):
    return crud.get_pazienti(db)

# Rotta per leggere i dati di un paziente da DB
@app.get("/pazienti/{id_paziente}", response_model=schemas.PazienteResponse)
def lista_paziente_by_id(id_paziente: int, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.admin, models.RuoloUtente.medico, models.RuoloUtente.paziente))):
    if cast(models.RuoloUtente, current_user.ruolo) == models.RuoloUtente.paziente and cast(int, current_user.id_account) != id_paziente:
        raise HTTPException(status_code=403, detail="Non puoi visualizzare i dati di un altro paziente.")

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
def update_paziente(id_paziente: int, aggiornamento_paziente: schemas.PazienteUpdate, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.admin, models.RuoloUtente.paziente))):
    if cast(models.RuoloUtente, current_user.ruolo) == models.RuoloUtente.paziente and cast(int, current_user.id_account) != id_paziente:
        raise HTTPException(status_code=403, detail="Non puoi modificare i dati di un altro paziente.")
    
    db_paziente = crud.get_paziente(db, id_paziente)

    if not db_paziente:
        raise HTTPException(status_code=404, detail="ID paziente non presente a sistema.")

    return crud.update_paziente(db, id_paziente, aggiornamento_paziente)

# Rotta per l'eliminazione di un paziente a DB tramite ID (PK)
@app.delete("/pazienti/{id_paziente}", response_model=schemas.PazienteResponse)
def delete_paziente(id_paziente: int, db: Session=Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.admin))):
    db_paziente = crud.delete_paziente(db, id_paziente)

    if not db_paziente:
        raise HTTPException(status_code=404, detail="ID paziente non presente a sistema.")

    return db_paziente

# Rotta per l'eliminazione di un paziente a DB tramite Codice Fiscale
@app.delete("/pazienti/cf/{codice_fiscale}", response_model=schemas.PazienteResponse)
def delete_paziente_by_cf(codice_fiscale: str, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.admin))):
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
def create_medico(medico: schemas.MedicoCreate, db: Session=Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.admin))):
    db_medico = crud.get_medico_by_matricola(db, matricola=medico.matricola)

    if db_medico:
        raise HTTPException(status_code=400, detail="Matricola già registrata a sistema.")
    
    return crud.create_medico(db, medico)

# Rotta per l'aggiornamento di un medico (payload parziale)
@app.patch("/medici/{id_medico}", response_model=schemas.MedicoResponse)
def update_medico(id_medico: int, aggiornamento_medico: schemas.MedicoUpdate, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.admin))):
    db_medico = crud.get_medico(db, id_medico)

    if not db_medico:
        raise HTTPException(status_code=404, detail="ID medico non presente a sistema.")

    return crud.update_medico(db, id_medico, aggiornamento_medico)

# Rotta per l'eliminazione di un medico a DB tramite ID (PK)
@app.delete("/medici/{id_medico}", response_model=schemas.MedicoResponse)
def delete_medico(id_medico: int, db: Session=Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.admin))):
    db_medico = crud.delete_medico(db, id_medico)

    if not db_medico:
        raise HTTPException(status_code=404, detail="ID medico non presente a sistema.")

    return db_medico

# Rotta per l'eliminazione di un medico a DB tramite matricola
@app.delete("/medici/matricola/{matricola}", response_model=schemas.MedicoResponse)
def delete_medico_by_matricola(matricola: str, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.admin))):
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
        raise HTTPException(status_code=404, detail="ID prestazione non presente a catalogo.")
    
    return db_prestazione   

# Rotta per inserire una nuova prestazione nel catalogo
@app.post("/prestazioni/", response_model=schemas.CatalogoPrestazioniResponse, status_code=201)
def create_prestazione(prestazione: schemas.CatalogoPrestazioniCreate, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.admin))):
    db_prestazione = crud.get_prestazione_by_nome(db, nome_visita=prestazione.nome_visita)

    if db_prestazione:
        raise HTTPException(status_code=400, detail="Prestazione già presente a catalogo.")

    return crud.create_prestazione(db, prestazione)

# Rotta per modificare una prestazione
@app.patch("/prestazioni/{id_prestazione}", response_model=schemas.CatalogoPrestazioniResponse)
def update_prestazione(id_prestazione: int, dati_aggiornamento: schemas.CatalogoPrestazioniUpdate, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.admin))):
    db_prestazione = crud.get_prestazione(db, id_prestazione)

    if not db_prestazione:
        raise HTTPException(status_code=404, detail="ID prestazione non presente a catalogo.")
    
    return crud.update_prestazione(db, id_prestazione, dati_aggiornamento)

# Rotta per cancellare una prestazione presente nel catalogo
@app.delete("/prestazioni/{id_prestazione}", response_model=schemas.CatalogoPrestazioniResponse)
def delete_prestazione(id_prestazione: int, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.admin))):
    db_prestazione = crud.delete_prestazione(db, id_prestazione)

    if not db_prestazione:
        raise HTTPException(status_code=404, detail="ID prestazione non presente a catalogo.")

    return db_prestazione
#endregion

#region PRENOTAZIONE
# Rotta per leggere tutte le prenotazioni presenti a sistema
@app.get("/prenotazioni/", response_model=list[schemas.PrenotazioneResponse])
def lista_prenotazioni(db: Session=Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.admin, models.RuoloUtente.medico))):
    return crud.get_prenotazioni(db)

# Rotta per leggere i dati di una singola prenotazione presente a DB
@app.get("/prenotazioni/{id_prenotazione}", response_model=schemas.PrenotazioneResponse)
def lista_prenotazione_by_id(id_prenotazione: int, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.admin, models.RuoloUtente.medico, models.RuoloUtente.paziente))):
    db_prenotazione = crud.get_prenotazione(db, id_prenotazione)

    if not db_prenotazione:
        raise HTTPException(status_code=404, detail="ID prenotazione non presente a sistema.")

    if cast(models.RuoloUtente, current_user.ruolo) == models.RuoloUtente.paziente and cast(int, db_prenotazione.id_paziente) != cast(int, current_user.id_account):
        raise HTTPException(status_code=403, detail="Non puoi visualizzare la prenotazione di un altro paziente.")
    
    return db_prenotazione

# Rotta per leggere tutte le prenotazioni di un singolo paziente
@app.get("/prenotazioni/paziente/{id_paziente}", response_model=list[schemas.PrenotazioneResponse])
def lista_prenotazioni_by_paziente(id_paziente: int, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.admin, models.RuoloUtente.medico, models.RuoloUtente.paziente))):
    if cast(models.RuoloUtente, current_user.ruolo) == models.RuoloUtente.paziente and cast(int, current_user.id_account) != id_paziente:
        raise HTTPException(status_code=403, detail="Non puoi visualizzare la prenotazione di un altro paziente.")

    if not crud.get_paziente(db, id_paziente):
        raise HTTPException(status_code=404, detail="ID paziente non presente a sistema.")

    return crud.get_prenotazioni_by_paziente(db, id_paziente)

# Rotta per leggere tutte le prenotazioni di un singolo medico
@app.get("/prenotazioni/medico/{id_medico}", response_model=list[schemas.PrenotazioneResponse])
def lista_prenotazioni_by_medico(id_medico: int, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.admin, models.RuoloUtente.medico))):
    if cast(models.RuoloUtente, current_user.ruolo) == models.RuoloUtente.medico and cast(int, current_user.id_account) != id_medico:
        raise HTTPException(status_code=403, detail="Non puoi visualizzare le prenotazioni di un altro medico.")

    if not crud.get_medico(db, id_medico):
        raise HTTPException(status_code=404, detail="ID medico non presente a sistema.")

    return crud.get_prenotazioni_by_medico(db, id_medico)

# Rotta per l'inserimento di una prenotazione a DB
@app.post("/prenotazioni/", response_model=schemas.PrenotazioneResponse, status_code=201)
def create_prenotazione(prenotazione: schemas.PrenotazioneCreate, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.admin, models.RuoloUtente.paziente))):
    if cast(models.RuoloUtente, current_user.ruolo) == models.RuoloUtente.paziente and cast(int, current_user.id_account) != prenotazione.id_paziente:
        raise HTTPException(status_code=403, detail="Non puoi creare una prenotazione per un altro paziente.")
    
    if not crud.get_paziente(db, prenotazione.id_paziente):
        raise HTTPException(status_code=404, detail="ID paziente non presente a sistema")
    
    if not crud.get_medico(db, prenotazione.id_medico):
        raise HTTPException(status_code=404, detail="ID medico non presente a sistema")
    
    db_prestazione = crud.get_prestazione(db, prenotazione.id_prestazione)
    if not db_prestazione:
        raise HTTPException(status_code=404, detail="ID prestazione non presente a sistema")

    db_duplicata = crud.get_prenotazione_duplicata(
        db,
        prenotazione.id_paziente,
        prenotazione.id_medico,
        prenotazione.id_prestazione,
        prenotazione.data_appuntamento
    )
    if db_duplicata:
        raise HTTPException(status_code=400, detail="Prenotazione già presente per questa data.")

    return crud.create_prenotazione(db, prenotazione, cast(float, db_prestazione.costo_base))

# Rotta per modificare una prenotazione
@app.patch("/prenotazioni/{id_prenotazione}", response_model=schemas.PrenotazioneResponse)
def update_prenotazione(id_prenotazione: int, dati_aggiornamento: schemas.PrenotazioneUpdate, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.admin, models.RuoloUtente.medico))):
    db_prenotazione = crud.get_prenotazione(db, id_prenotazione)

    if not db_prenotazione:
        raise HTTPException(status_code=404, detail="ID prenotazione non presente a sistema.")

    if dati_aggiornamento.costo_applicato is not None:
        db_prestazione = crud.get_prestazione(db, cast(int, db_prenotazione.id_prestazione))
        if db_prestazione and dati_aggiornamento.costo_applicato > cast(float, db_prestazione.costo_base):
            raise HTTPException(
                status_code=400,
                detail=f"Il costo applicato non può superare il costo base a catalogo ({db_prestazione.costo_base} €)."
            )

    return crud.update_prenotazione(db, id_prenotazione, dati_aggiornamento)

# Rotta per cancellare una prenotazione presente nel sistema
@app.delete("/prenotazioni/{id_prenotazione}", response_model=schemas.PrenotazioneResponse)
def delete_prenotazione(id_prenotazione: int, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.admin, models.RuoloUtente.paziente))):
    db_prenotazione = crud.get_prenotazione(db, id_prenotazione)

    if not db_prenotazione:
        raise HTTPException(status_code=404, detail="ID prenotazione non presente a sistema.")

    if cast(models.RuoloUtente, current_user.ruolo) == models.RuoloUtente.paziente and cast(int, db_prenotazione.id_paziente) != cast(int, current_user.id_account):
        raise HTTPException(status_code=403, detail="Non puoi cancellare la prenotazione di un altro paziente.")

    return crud.delete_prenotazione(db, id_prenotazione)

#region REFERTO
# Rotta per leggere tutti i referti presenti a sistema (con paginazione)
@app.get("/referti/", response_model=list[schemas.RefertoResponse])
def lista_referti(skip: int = 0, amount: int = 100, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.medico))):
    return crud.get_referti(db, skip, amount)

# Rotta per leggere un singolo referto tramite ID
@app.get("/referti/{id_referto}", response_model=schemas.RefertoResponse)
def lista_referto_by_id(id_referto: int, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.medico, models.RuoloUtente.paziente))):
    db_referto = crud.get_referto(db, id_referto)

    if not db_referto:
        raise HTTPException(status_code=404, detail="ID referto non presente a sistema.")

    if cast(models.RuoloUtente, current_user.ruolo) == models.RuoloUtente.paziente:
        db_prenotazione = crud.get_prenotazione(db, cast(int, db_referto.id_prenotazione))
        if not db_prenotazione or cast(int, db_prenotazione.id_paziente) != cast(int, current_user.id_account):
            raise HTTPException(status_code=403, detail="Non puoi visualizzare il referto di un altro paziente.")

    return db_referto

# Rotta per leggere il referto associato a una specifica prenotazione
@app.get("/referti/prenotazione/{id_prenotazione}", response_model=schemas.RefertoResponse)
def lista_referto_by_prenotazione(id_prenotazione: int, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.medico, models.RuoloUtente.paziente))):
    db_prenotazione = crud.get_prenotazione(db, id_prenotazione)
    if not db_prenotazione:
        raise HTTPException(status_code=404, detail="ID prenotazione non presente a sistema.")

    if cast(models.RuoloUtente, current_user.ruolo) == models.RuoloUtente.paziente and cast(int, db_prenotazione.id_paziente) != cast(int, current_user.id_account):
        raise HTTPException(status_code=403, detail="Non puoi visualizzare il referto di un altro paziente.")

    db_referto = crud.get_referto_by_id_prenotazione(db, id_prenotazione)
    if not db_referto:
        raise HTTPException(status_code=404, detail="Nessun referto emesso per questa prenotazione.")

    return db_referto

# Rotta per leggere tutti i referti emessi in una specifica data
@app.get("/referti/data/{data_emissione}", response_model=list[schemas.RefertoResponse])
def lista_referti_by_data(data_emissione: date, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.medico))):
    return crud.get_referti_by_data_emissione(db, data_emissione)

# Rotta per creare un nuovo referto
@app.post("/referti/", response_model=schemas.RefertoResponse, status_code=201)
def create_referto(referto: schemas.RefertoCreate, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.medico))):
    if not crud.get_prenotazione(db, referto.id_prenotazione):
        raise HTTPException(status_code=404, detail="ID prenotazione non presente a sistema.")

    if crud.get_referto_by_id_prenotazione(db, referto.id_prenotazione):
        raise HTTPException(status_code=400, detail="Referto già presente per questa prenotazione.")

    return crud.create_referto(db, referto)

# Rotta per modificare un referto esistente
@app.patch("/referti/{id_referto}", response_model=schemas.RefertoResponse)
def update_referto(id_referto: int, dati_aggiornamento: schemas.RefertoUpdate, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.medico))):
    db_referto = crud.update_referto(db, id_referto, dati_aggiornamento)

    if not db_referto:
        raise HTTPException(status_code=404, detail="ID referto non presente a sistema.")

    return db_referto

# Rotta per cancellare un referto a sistema
@app.delete("/referti/{id_referto}", response_model=schemas.RefertoResponse)
def delete_referto(id_referto: int, db: Session = Depends(get_db), current_user: models.Account = Depends(security.require_roles(models.RuoloUtente.admin))):
    db_referto = crud.delete_referto(db, id_referto)

    if not db_referto:
        raise HTTPException(status_code=404, detail="ID referto non presente a sistema.")

    return db_referto
#endregion