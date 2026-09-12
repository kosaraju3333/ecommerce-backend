from app.database import SessionLocal
from app.models.user import User
from app.utils.security import hash_password


db = SessionLocal()

admin = User(
    username="admin",
    email="admin@store.com",
    password_hash=hash_password("admin123"),
    role="ADMIN"
)

db.add(admin)
db.commit()
db.refresh(admin)

print("Admin created successfully!")
print("Username:", admin.username)
print("Role:", admin.role)

db.close()