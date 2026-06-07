import bcrypt
from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.models import Base, User

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> bool:
    try:
        Base.metadata.create_all(bind=engine)
        _seed_demo_users()
    except SQLAlchemyError:
        return False

    return True


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


_DEMO_USER_SEEDS = [
    {"id": "user-atul", "email": "atul@enterprise.ai", "name": "Atul", "role": "admin", "department": "IT", "password": "atul123"},
    {"id": "user-analyst", "email": "analyst@enterprise.ai", "name": "Enterprise Analyst", "role": "analyst", "department": "Operations", "password": "analyst123"},
    {"id": "user-employee", "email": "employee@enterprise.ai", "name": "Enterprise Employee", "role": "employee", "department": "HR", "password": "employee123"},
    {"id": "user-viewer", "email": "viewer@enterprise.ai", "name": "Enterprise Viewer", "role": "viewer", "department": "Security", "password": "viewer123"},
]


def _seed_demo_users() -> None:
    try:
        with SessionLocal() as session:
            for seed in _DEMO_USER_SEEDS:
                exists = session.execute(
                    select(User).where(User.email == seed["email"])
                ).scalars().first()
                if exists is None:
                    session.add(User(
                        id=seed["id"],
                        email=seed["email"],
                        name=seed["name"],
                        role=seed["role"],
                        department=seed["department"],
                        password_hash=hash_password(seed["password"]),
                    ))
            session.commit()
    except SQLAlchemyError:
        return
