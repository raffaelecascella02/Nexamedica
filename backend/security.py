import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import models
from database import get_db

# Carica eventuali variabili d'ambiente dal file .env
load_dotenv()

# Configurazione parametri JWT
SECRET_KEY = os.getenv("SECRET_KEY", "nexamedica-dev-secret-key-cambia-in-prod-32bytes")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Schema OAuth2 per l'estrazione del token Bearer dall'header Authorization (e pulsante Authorize su Swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#region HASHING PASSWORD
# Genera l'hash bcrypt della password in chiaro
def get_password_hash(password: str):
    encoded_password = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(encoded_password, salt).decode("utf-8")

# Verifica la corrispondenza tra password in chiaro e hash salvato a DB
def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )
#endregion

#region JWT E RBAC
# Crea e firma un nuovo token JWT con scadenza UTC
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Decodifica il token JWT e restituisce l'account autenticato da DB
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Credenziali non valide o token scaduto.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub") # legge il "subject" (standard RFC 7519) per ID utente 
        if not sub:
            raise credentials_exception
        account_id = int(sub)
    except (InvalidTokenError, ValueError):
        raise credentials_exception

    db_account = db.query(models.Account).filter(models.Account.id_account == account_id).first()
    if not db_account:
        raise credentials_exception

    return db_account

# Dependency factory per verificare che il ruolo dell'utente sia tra quelli autorizzati
def require_roles(*ruoli_ammessi: models.RuoloUtente):
    def role_checker(current_user: models.Account = Depends(get_current_user)):
        if   current_user.ruolo not in ruoli_ammessi:
            raise HTTPException(status_code=403, detail="Permessi insufficienti per questa operazione.")
        return current_user

    return role_checker
#endregion