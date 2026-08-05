from app.auth.hashing import hash_password, verify_password

password = "MyPassword@123"

hashed = hash_password(password)

print("Hashed Password:")
print(hashed)

print()

print("Verification:")
print(verify_password(password, hashed))