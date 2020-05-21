import cv2 # OpenCV 2
import numpy as np 
import time as t
import random
from Crypto.Cipher import AES  # AES 128bits (16 Bytes)
from Crypto.Util.Padding import pad, unpad  #for pakage the info
from algoritmos_seguridad import AESCifrador
from algoritmos_seguridad import AppRSA
from algoritmos_seguridad import AESDescifrador
from stegano_code import Stegano

def abrir_archivo(ruta):
    with open(ruta, 'rb') as txt:
        plain_text_Bytes = txt.read()
        plain_text = str(plain_text_Bytes)
    return plain_text_Bytes

def guardar_archivo(ruta, t_bytes):
    with open(ruta, 'wb') as txt:
        txt.write(t_bytes)
        pass


input_image = "example.jpg"
input_file = "example.txt"
output_image = "encoded_image.PNG"

plain_text_Bytes = abrir_archivo(input_file)

# RSA
apprsa = AppRSA()
# Genera clave publica y privada local (se trabajara localmente en este ejemplo)
clave_publica, clave_privada = apprsa.generar_claves()
apprsa.otra_clave_publica = clave_publica


# Obtiene la clave de sesion
cifrador = AESCifrador()
cifrador.hashear_clave("miclavesesion")
clave_sesion = cifrador.clave_sesion


###########ENCODE
encoder = Stegano(input_image)

full_txt_relleno = encoder.agregar_relleno(plain_text_Bytes)

# Algoritmo AES CBC
#cipher_text_Bytes, iv, size_text_total, bits_same= cifrar_txt_relleno (plain_text, img, clave_sesion)

cifrador.plain_text_Bytes = full_txt_relleno

texto_cifrado, iv = cifrador.cifrar_archivo()

cs_c = apprsa.cifrar_clave(clave_sesion)

iv_c = apprsa.cifrar_clave(iv)


full_content = apprsa.otra_clave_publica + cs_c + iv_c + texto_cifrado
#full_content = cs_c + iv_c + texto_cifrado

#tc = texto_cifrado ###################TEMP

#print(f"\nCS_C : {cs_c}\n\n IV_C : {iv_c}\n")


with open ("zfull_content_bstr.txt", 'w') as f:
    f.write(str(full_content))

with open ("zfull_content_bytes.txt", 'wb') as f:
    f.write(full_content)

print("\n[+] Información Inicial...\n")
print(f"Texto Cifrado: AES(Texto+Relleno) = {len(texto_cifrado)}     -> Siempre es Texto+Relleno + 1")
print(f"cs_c_len: {len(cs_c)}")
print(f"iv_c_len: {len(iv_c)}")
print(f"Full Content Length: (cs_c+iv_c+texto_cifrado) = {len(full_content)}")
print(f"Input Image Length: {encoder.n_bytes}")
print(f"Public key length: {len(apprsa.otra_clave_publica)}\n\n")


   
# encode the data into the image
encoded_image = encoder.encode(full_content)
# save the output image (encoded image)
cv2.imwrite(output_image, encoded_image)


###########DECODE
decoder = Stegano(output_image)
decoder.show_entropy2()
    
# decode the secret data from the image
decoded_data = decoder.decode()

decoded_data_bytes = decoded_data.encode("latin1")

with open ('zdecoded_data_bstr.txt','w') as f:
    f.write(str(decoded_data_bytes))

opk = decoded_data_bytes[:450]
cs_c = decoded_data_bytes[450:706]
iv_c = decoded_data_bytes[706:962]

#cs_c = decoded_data_bytes[:256]
#iv_c = decoded_data_bytes[256:512]

# Valor para obtener el limite del texto cifrado original. 
sum_mod = len(decoded_data_bytes)%16-2

#texto_cifrado = decoded_data_bytes[512:len(decoded_data_bytes)-sum_mod]
texto_cifrado = decoded_data_bytes[962:len(decoded_data_bytes)-sum_mod]

#print(f"\nOtra clave publica len {len(opk)}\n")

#print(f"\nOtra clave publica: {opk}\n")


print("\n[+] Información Recibida...\n")


print(f"Input Image Length: {len(decoded_data_bytes)}")

print(f"Texto Cifrado: {len(texto_cifrado)}")
print(f"cs_c_len: {len(cs_c)}")
print(f"iv_c_len: {len(iv_c)}")
print(f"Received Public key length: {len(opk)}\n\n")


#print(f"Texto Cifrado: {(len(texto_cifrado)-16)}")

#print(f"decoded_data_bytes: {len(decoded_data_bytes)}")



#print(f"\nCS_C : {cs_c}\n\n IV_C : {iv_c}\n")


cs_d = apprsa.descifrar_clave(cs_c)
iv_d = apprsa.descifrar_clave(iv_c)


descifrador = AESDescifrador()
descifrador.clave_sesion_descifrada = cs_d
descifrador.iv_descifrado = iv_d
descifrador.texto_cifrado = texto_cifrado
texto_descifrado = descifrador.descifrar_archivo()

guardar_archivo("zdecoded_data.txt", texto_descifrado)
