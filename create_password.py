import bcrypt

password = b"mysecretpassword"  # Original password (in bytes)
hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

# Convert hashed password to string to store in .env
print(hashed_password.decode('utf-8'))