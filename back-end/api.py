import ssl
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import os

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

@app.post("/auth")
def authenticate(auth: AuthRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.username == auth.username).first()
    db.close()

    if user and user.password == auth.password:
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
