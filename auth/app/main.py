from fastapi import FastAPI, Depends
from app.core.database import engine, Base, get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.endpoints import auth, users, admin_users
from app.models.user import User, UserRole
from app.core.security import get_password_hash
import time

# Creación del esquema 'auth' si no existe en la base de datos
with engine.connect() as con:
    con.execute(text("CREATE SCHEMA IF NOT EXISTS auth"))
    con.commit()

# Generación de tablas basadas en los modelos definidos
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")

@app.on_event("startup")
def create_initial_data():
    """
    Función de arranque para preparar datos iniciales y parches de emergencia.
    """
    # Asegura que la columna 'username' exista en la tabla de usuarios (parche migración manual)
    try:
        with engine.connect() as con:
            con.execute(text("ALTER TABLE auth.users ADD COLUMN IF NOT EXISTS username VARCHAR UNIQUE"))
            con.commit()
    except Exception:
        pass 
        
    # LÓGICA DE EMERGENCIA / SEEDING PARA ADMINISTRADOR (HU-12)
    # Esta sección asegura que el usuario admin@territorial.com siempre tenga privilegios.
    try:
        with engine.connect() as conn:
            with conn.begin():
                # Forzamos que admin@territorial.com sea ADMIN y tenga la contraseña 'Admin123!'
                # Usamos SQL directo para evitar conflictos con cachés de ORM o Enums.
                conn.execute(text("""
                    UPDATE auth.users 
                    SET role = 'ADMIN', hashed_password = :hp, is_active = true 
                    WHERE email = 'admin@territorial.com'
                """), {"hp": get_password_hash("Admin123!")})
                
                # Si el usuario administrador no existe en absoluto, lo creamos.
                conn.execute(text("""
                    INSERT INTO auth.users (email, hashed_password, role, is_active)
                    SELECT 'admin@territorial.com', :hp, 'ADMIN', true
                    WHERE NOT EXISTS (SELECT 1 FROM auth.users WHERE email = 'admin@territorial.com')
                """), {"hp": get_password_hash("Admin123!")})
    except Exception as e:
        print(f"Error en seeding inicial: {e}")

# --- REGISTRO DE RUTAS ---

# Rutas estándar de autenticación (Login, Registro)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

# Módulo de Gestión de Usuarios (HU-12) - Solo accesible por administradores
app.include_router(admin_users.router, prefix="/api/v1/admin/users", tags=["admin-users"])

@app.get("/health")
def health_check():
    """
    Endpoint de salud para que el Gateway y el monitoreo verifiquen el servicio.
    Verifica también la conexión a la base de datos.
    """
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
