import bcrypt

password = 'demo123'
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print('Hashed password for demo123:', hashed.decode('utf-8'))
