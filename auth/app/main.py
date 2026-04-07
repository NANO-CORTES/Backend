from fastapi import FastAPI, Depends
from app.core.database import engine, Base, get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.endpoints import auth, users
from app.models.user import User, UserRole
from app.core.security import get_password_hash
import time

# Create schema if not exists
with engine.connect() as con:
    con.execute(text("CREATE SCHEMA IF NOT EXISTS auth"))
    con.commit()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")

@app.on_event("startup")
def create_initial_data():
    # Manually ensure username column exists for existing tables
    try:
        with engine.connect() as con:
            con.execute(text("ALTER TABLE auth.users ADD COLUMN IF NOT EXISTS username VARCHAR UNIQUE"))
            con.commit()
    except Exception:
        pass # It might already exist or schema not yet ready
        
    db = next(get_db())
    admin_exists = db.query(User).filter(User.email == "admin@territorial.com").first()
    if not admin_exists:
        admin_user = User(
            email="admin@territorial.com",
            username="admin",
            password_hash=get_password_hash("admin123"),
            full_name="System Admin",
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin_user)
        db.commit()

app.include_router(auth.router, tags=["auth"])
app.include_router(users.router, prefix="/admin/users", tags=["admin"])

@app.get("/health")
def health_check():
    try:
        with engine.connect() as con:
            con.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False
        
    return {
        "status": "healthy" if db_connected else "unhealthy",
        "service_name": "ms-auth",
        "version": "1.0.0",
        "db_connected": db_connected,
        "timestamp": int(time.time())
    }
