from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base, SessionLocal
from app.core.security import hash_password
from app.models.user import User, RoleEnum
from app.api.endpoints import auth, admin_users

app = FastAPI(title="ms-auth", version="1.0.0")

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(admin_users.router)


@app.on_event("startup")
def on_startup():
    """Create tables and seed the initial admin user if it doesn't exist."""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@territorial.com").first()
        if admin is None:
            seed_admin = User(
                email="admin@territorial.com",
                full_name="Administrador",
                password_hash=hash_password("Admin123!"),
                role=RoleEnum.ADMIN,
                is_active=True,
            )
            db.add(seed_admin)
            db.commit()
            print("✅ Usuario ADMIN semilla creado: admin@territorial.com / Admin123!")
        else:
            print("ℹ️  Usuario ADMIN semilla ya existe.")
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "ms-auth is running"}
