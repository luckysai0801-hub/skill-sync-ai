import os
import sys

# Ensure 'backend' package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from utils.password_utils import hash_password, verify_password
from models.user import UserRole

print("Testing direct bcrypt hash...")
plain = "TestPassword123!"
hashed = hash_password(plain)
print(f"Hashed: {hashed}")
is_valid = verify_password(plain, hashed)
print(f"Verify matches: {is_valid}")

print("\nTesting direct DB insert...")
from database import SessionLocal
from models.user import User

db = SessionLocal()
try:
    existing = db.query(User).filter(User.email == "test_direct@example.com").first()
    if existing:
        db.delete(existing)
        db.commit()

    new_user = User(
        email="test_direct@example.com",
        name="Direct Test User",
        password_hash=hashed,
        role=UserRole.candidate,
        email_verified=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    print(f"Successfully created user in DB with ID: {new_user.id}")
except Exception as e:
    print(f"DB Error: {e}")
finally:
    db.close()
