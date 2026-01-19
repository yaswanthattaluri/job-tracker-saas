from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI(title="Job Tracker API")

engine = create_engine(
    "sqlite:///./app.db",
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    company = Column(String, index=True)
    role = Column(String)
    status = Column(String, default="applied")  # applied/interview/offer/rejected
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class ApplicationCreate(BaseModel):
    company: str
    role: str
    status: str = "applied"

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/applications")
def create_application(payload: ApplicationCreate):
    db = SessionLocal()
    try:
        a = Application(company=payload.company, role=payload.role, status=payload.status)
        db.add(a)
        db.commit()
        db.refresh(a)
        return {"id": a.id, "company": a.company, "role": a.role, "status": a.status}
    finally:
        db.close()

@app.get("/applications")
def list_applications():
    db = SessionLocal()
    try:
        rows = db.query(Application).order_by(Application.created_at.desc()).all()
        return [
            {
                "id": r.id,
                "company": r.company,
                "role": r.role,
                "status": r.status,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
    finally:
        db.close()
