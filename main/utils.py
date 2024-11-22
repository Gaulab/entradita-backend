# entraditaBack/main/utils.py

import hashlib

def generate_qr_payload(owner_name, owner_lastname, owner_dni, timestamp):
    # Crea un string único con la información del dueño
    unique_string = f"{owner_name}{owner_lastname}{owner_dni}{timestamp}"
    
    # Genera un hash SHA256 del string único
    qr_payload = hashlib.sha256(unique_string.encode()).hexdigest()
    
    return qr_payload
