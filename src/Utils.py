from threading import Lock
from enum import Enum
import random
import threading
import time

RED     = '31m'
GREEN   = '32m'
YELLOW  = '33m'
BLUE    = '34m'
MAGENTA = '35m'
CIAN    = '36m'
WHITE   = '37m'

def print_address_bin(address):
    # Convert to binary and remove '0b' prefix
    binary_string = bin(address)[2:]
    # Pad with leading zeroes up to 3 bits
    binary_number = '{0:03}'.format(int(binary_string))
    return binary_number

def print_data_hex(data):
    hex_str = hex(data)[2:].zfill(2)
    return '0x'+hex_str

# Enumeración para los posibles estados de un bloque
class State(Enum):
    INVALID = 0
    SHARED = 1
    EXCLUSIVE = 2
    MODIFIED = 3
    OWNED = 4

# Enumeración de tipos de mensaje para el bus
class MessageType(Enum):
    RdReq = 0   # Solicitud de lectura
    RdResp = 1  # Respuesta a solicitud de lectura
    WrReq = 2   # Solicitud de escritura
    Inv = 3     # Invaliación de bloque
    WB = 4      # Write back (escritura a la memoria principal)