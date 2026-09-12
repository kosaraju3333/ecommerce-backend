from app.database import SessionLocal
from app.models.user import User
from app.utils.security import hash_password


db = SessionLocal()

customer = User(
    username="customer1",
    email="customer@store.com",
    password_hash=hash_password("customer123"),
    role="CUSTOMER"
)

db.add(customer)
db.commit()
db.refresh(customer)

print("Customer created successfully!")
print("Username:", customer.username)
print("Role:", customer.role)

db.close()