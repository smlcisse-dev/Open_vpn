import os
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from passlib.context import CryptContext

# =========================
# CONFIGURATION
# =========================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'users.db')}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Vérifie les dossiers nécessaires
FLAGS_DIR = os.path.join(BASE_DIR, "flags")
CONFIG_DIR = os.path.join(BASE_DIR, "client-configs")

os.makedirs(FLAGS_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

app = FastAPI()

# Servir les fichiers statiques (drapeaux et fichiers .ovpn)
app.mount("/flags", StaticFiles(directory=FLAGS_DIR), name="flags")
app.mount("/client-configs", StaticFiles(directory=CONFIG_DIR), name="client-configs")

# =========================
# UTILITAIRES
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# =========================
# MODELS SQLALCHEMY
# =========================

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class Country(Base):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    flag_path = Column(String)

class Server(Base):
    __tablename__ = "servers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    ovpn_path = Column(String)
    country_id = Column(Integer)

Base.metadata.create_all(bind=engine)

# =========================
# SCHÉMAS Pydantic
# =========================

class AuthRequest(BaseModel):
    username: str
    password: str

class CountryResponse(BaseModel):
    id: int
    name: str
    flag_path: str

    class Config:
        from_attributes = True

class ServerResponse(BaseModel):
    id: int
    name: str
    ovpn_path: str
    country_id: int

    class Config:
        from_attributes = True

# =========================
# ROUTES API
# =========================

@app.post("/auth")
def authenticate(auth: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == auth.username).first()
    if user and verify_password(auth.password, user.password):
        return {"message": "Authentification réussie"}
    raise HTTPException(status_code=401, detail="Identifiants invalides")

@app.post("/register")
def register(auth: AuthRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == auth.username).first():
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")
    hashed_password = get_password_hash(auth.password)
    user = User(username=auth.username, password=hashed_password)
    db.add(user)
    db.commit()
    return {"message": "Inscription réussie"}

@app.get("/countries", response_model=list[CountryResponse])
def list_countries(request: Request, db: Session = Depends(get_db)):
    countries = db.query(Country).all()
    base_url = str(request.base_url).rstrip("/")
    for country in countries:
        if not country.flag_path.startswith("http"):
            country.flag_path = f"{base_url}{country.flag_path}"
    return countries

@app.get("/servers/{country_id}", response_model=list[ServerResponse])
def list_servers(country_id: int, db: Session = Depends(get_db)):
    return db.query(Server).filter(Server.country_id == country_id).all()

# =========================
# INITIALISATION UNIQUES
# =========================

def init_db():
    db = SessionLocal()
    if not db.query(User).filter_by(username="user").first():
        user = User(username="user", password=get_password_hash("pass"))
        db.add(user)
        db.commit()
    db.close()

def init_vpn_data():
    db = SessionLocal()

    france = Country(name="France", flag_path="/flags/france.png")
    usa = Country(name="USA", flag_path="/flags/usa.png")
    db.add_all([france, usa])
    db.commit()

    db.refresh(france)
    db.refresh(usa)

    fr_server1 = Server(name="FR Server 1", ovpn_path="/client-configs/fr_server1.ovpn", country_id=france.id)
    us_server1 = Server(name="US Server 1", ovpn_path="/client-configs/us_server1.ovpn", country_id=usa.id)
    db.add_all([fr_server1, us_server1])
    db.commit()
    db.close()

# =========================
# À DÉCOMMENTER UNE FOIS :
# =========================

# init_db()
# init_vpn_data()
