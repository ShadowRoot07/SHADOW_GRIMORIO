import hashlib
clave = "SH4D0W_ARC4N3_X07"
print(f"Tu Hash Real: {hashlib.sha256(clave.strip().encode()).hexdigest()}")

