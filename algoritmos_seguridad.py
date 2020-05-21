import random
from Crypto.Cipher import AES, PKCS1_OAEP  # AES 128bits (16 Bytes)
from Crypto.Util.Padding import pad, unpad  #for pakage the info
from Crypto.PublicKey import RSA
import hashlib

class AppRSA():
    def __init__(self):
        # Clave pública local
        self.clave_publica = None
        # Clave privada local
        self.clave_privada = None
        # Clave pública del destinatario
        self.otra_clave_publica = None
        # Indica si el peer actual ha intercambiado su clave pública
        self.intercambio = False

    # Genera la clave pública y privada mediante RSA
    def generar_claves(self):
        key = RSA.generate(2048)
        self.clave_privada = key.export_key()
        self.clave_publica = key.publickey().export_key()
        return self.clave_publica, self.clave_privada

    # Cifra una clave (como la clave de sesión o última subclave)
    # a partir de la clave pública del destinatario
    def cifrar_clave(self, clave):
        # Obtiene la clave RSA publica del destinatario
        recipient_key = RSA.import_key(self.otra_clave_publica)

        # Cifra la clave ingresada con la clave RSA publica del otro
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        clave_cifrada = cipher_rsa.encrypt(clave)
        return clave_cifrada

    # Descifra una clave recibida (como la clave de sesión cifrada o última subclave cifrada)
    # a partir de mi clave privada
    def descifrar_clave(self, clave_cifrada):
        # Descifra la clave de sesión con la clave RSA privada
        p_key = RSA.import_key(self.clave_privada)
        cipher_rsa = PKCS1_OAEP.new(p_key)
        clave = cipher_rsa.decrypt(clave_cifrada)
        return clave


class AESCifrador():
    def __init__(self):
        # Clave de sesión actual
        self.clave_sesion = None
        # Texto plano en string
        self.plain_text = None
        # Texto plano en bytes
        self.plain_text_Bytes = None
        # Texto cifrado
        self.texto_cifrado = None
        # Última subclave
        self.iv = None
        # Última subclave cifrada
        self.iv_cifrado = None
        # Clave de sesión cifrada
        self.clave_sesion_cifrada = None
        # Información a enviar
        self.informacion_a_enviar = None
        # Indica si se ha recibido un mensaje 
        self.recibir_mensaje = False
        
    # Obtiene el hash de la clave de sesión a partir del texto ingresado
    def hashear_clave(self, txt):
        # Obtiene la sal a partir de una cadena de caracteres aleatoria del tamaño del texto
        salt = ''.join([chr(random.randint(65, 122)) for i in range(len(txt))])
        # Realiza la operación XOR entre la sal y el texto
        key = [chr(ord(a) ^ ord(b)) for a,b in zip(txt, salt)]
        # Pasa a bytes la nueva cadena de caracteres
        key = bytes(''.join(key),"utf-8")
        # Obtiene el digest de 16 bytes
        print(f"    [*] Clave con Sal: {key}")
        digest = hashlib.md5(key).digest()
        #hexdigest = hashlib.md5(txt).hexdigest() # 32 character hexadecimal
        print(f"    [*] Digest: {digest}")
        self.clave_sesion = digest      
        return self.clave_sesion
            
    # Cifra el archivo ingresado mediante AES CBC. Retorna el texto cifrado y la última subclave
    def cifrar_archivo(self):
        cipher = AES.new(self.clave_sesion, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(self.plain_text_Bytes, AES.block_size))
        self.iv = cipher.iv
        self.texto_cifrado = ct_bytes
        return ct_bytes, cipher.iv
        

class AESDescifrador():
    def __init__(self):
        # Texto cifrado recibido
        self.texto_cifrado = None
        # Última subclave descifrada
        self.iv_descifrado = None
        # Última subclave cifrada recibida
        self.iv_cifrado = None
        # Clave de sesión cifrada recibida
        self.clave_sesion_cifrada = None
        # Clave de sesión descifrada
        self.clave_sesion_descifrada = None
        # Texto plano descifrado
        self.texto_descifrado = None
        # Información recibida
        self.informacion_recibida = None

    # Descifra el archivo ingresado mediante AES CBC. Retorna el texto descifrado.
    def descifrar_archivo(self):
        cipher = AES.new(self.clave_sesion_descifrada, AES.MODE_CBC, self.iv_descifrado)
        self.texto_descifrado = unpad(cipher.decrypt(self.texto_cifrado), AES.block_size)

        return self.texto_descifrado

