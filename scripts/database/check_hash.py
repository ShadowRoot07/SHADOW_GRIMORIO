import hashlib

# Esta es la clave que estamos usando
clave_maestra = "ejemplo"

# Generamos el hash SHA-256
hash_generado = hashlib.sha256(clave_maestra.strip().encode()).hexdigest()

print("\n" + "="*40)
print(f"CLAVE: {clave_maestra}")
print(f"HASH REAL: {hash_generado}")
print("="*40 + "\n")
print("Copia el 'HASH REAL' y pégalo en ROOT_HASH_TARGET")

