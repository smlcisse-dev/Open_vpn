import ssl
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

app = FastAPI()

# Base SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'users.db')}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class AuthRequest(BaseModel):
    username: str
    password: str

# Check password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@app.post("/auth")
def authenticate(auth: AuthRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.username == auth.username).first()
    db.close()

    if user and verify_password(auth.password, user.password):
        return {"message": "Authentification réussie"}
    else:
        raise HTTPException(status_code=401, detail="Identifiants invalides")

# Fonction à appeler une seule fois pour ajouter un utilisateur de test
def init_db():
    db = SessionLocal()
    if not db.query(User).filter_by(username="user").first():
        user = User(username="user", password="pass")
        db.add(user)
        db.commit()
    db.close()

# Décommente cette ligne une fois pour créer l'utilisateur, puis re-commente-la
# init_db()

# Registration
@app.post("/register")
def register(auth: AuthRequest):
    db = SessionLocal()
    if db.query(User).filter(User.username == auth.username).first():
        db.close()
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")
    hashed_password = get_password_hash(auth.password)
    user = User(username=auth.username, password=hashed_password)
    db.add(user)
    db.commit()
    db.close()
    return {"message": "Inscription réussie"}
