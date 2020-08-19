import cv2
import numpy as np
import random


class Stegano:
    def __init__(self):
        # Imagen original
        self.image = None
        # Tamaño de la imagen
        self.n_bytes = None
        # Datos secretos a codificar
        self.secret_data = None     
        # Entropía de la imagen original
        self.image_entropy = None
        # Nueva imagen con los datos secretos codificados
        self.newimage = None
        # Entropía de la nueva imagen
        self.newimage_entropy = None
    
    # Lee y asigna variables de la imagen original
    def read_image(self, ruta):
        # Lee la imagen
        self.image = cv2.imread(ruta) 
        # Variable que indica el número máximo de bytes a codificar
        self.n_bytes = self.image.shape[0] * self.image.shape[1] * 3 // 8 
        # Entropía de la imagen original
        self.image_entropy = self.show_entropy(cv2.imread(ruta))
    
    # Asignación de variables de la imagen recibida
    def receive_image(self, img):
        # Recibe la imagen del otro peer
        self.image = img
        # Variable que indica el número de bytes codificados
        self.n_bytes = self.image.shape[0] * self.image.shape[1] * 3 // 8 
        # Entropía de la imagen recibida
        self.image_entropy = self.show_entropy(img) 

    # Convierte varios tipos de datos a binario
    def to_bin(self, data):
        if isinstance(data, str):                                   # Convierte string a binario
            return ''.join([ format(ord(i), "08b") for i in data ])
        elif isinstance(data, bytes):                               # Convierte bytes a binario
            return ''.join([ format(i, "08b") for i in data ])
        elif isinstance(data, np.ndarray):                          # Convierte arreglo de numpy (imagen) a binario
            return [ format(i, "08b") for i in data ]
        elif isinstance(data, int) or isinstance(data, np.uint8):   # Convierte entero a binario
            return format(data, "08b")
        else:
            raise TypeError("Type not supported.")

    # Verifica que el tamaño del texto plano sea menor a la capacidad de la imagen
    def check_size(self, data):
        if len(data)+512 > self.n_bytes:
            return False
        return True

    # Agrega una cadena aleatoria al texto plano 
    def agregar_relleno(self, plain_text):
        print("[+] Agregando Cadena Aleatoria...")
        # Define separador entre el texto plano y la cadena aleatoria
        plain_text += b"===="
        # Obtiene longitud que tendrá de la cadena aleatoria
        length_random_str = self.n_bytes - (len(plain_text) + 512) # Le suma 512, el cual es el tamaño del cs y iv cifrado
                                                                       # Le suma longitud 64, del tamaño del texto cifrado+relleno
       
        # Se modifica la longitud del string aleatorio para que el módulo de la suma con el texto plano
        # siempre sea el valor de 15 mod 16. Esto se hace para que al hacer el algoritmo AES, siempre
        # el tamaño de bytes total sea 1 más que el del tamaño original.
        
        # Todo esto se hace para que posteriormente se pueda obtener el límite del texto cifrado sin
        # necesidad de utilizar headers que lo indiquen, sino sólamente restandole los valores que
        # faltan según el tamaño de la imagen % 16.
        while (length_random_str+len(plain_text)) % 16 != 0:
            length_random_str -= 1
        length_random_str -= 1

        # Variable para imprimir que indica el tamaño que tendrá el texto con el relleno
        str_resta=length_random_str+len(plain_text)
        print_str=f"    [*]Texto+Relleno: Texto({len(plain_text)}) + Relleno({length_random_str}) = {str_resta}"
        
        # Genera cadena aleatoria de caracteres
        random_str = np.zeros(length_random_str, dtype=np.uint8)
        random_chain = []
        for i in range(0,length_random_str):                   
            random_str[i] = random.randint(65, 122)
        random_chain = ''.join(chr(i) for i in random_str)

        # Codifica la cadena aleatoria en latin1 y la agrega al texto plano
        plain_text = plain_text + random_chain.encode("latin1")
        
        # Guarda la variable de la información secreta
        self.secret_data = plain_text
        
        return plain_text, print_str

    # Utiliza el Algoritmo LSB para codificar la información secreta
    def encode(self, secret_data):
        self.secret_data = secret_data
        
        data_index = 0

        # Convierte los datos a binario
        binary_secret_data = self.to_bin(secret_data)
        
        # Tamaño de los datos a ocultar
        data_len = len(binary_secret_data)

        # Recorre cada fila, pixel y canal de la imagen, quitando el último bit del binario y agregando el de los datos
        for row in self.image:
            for pixel in row:
                for ch in range(len(pixel)):    # ch representa el canal, (R,G,B)
                    if data_index < data_len:
                        # pixel[ch] :: Pixel en el canal R, G o B. Es un valor de 0 a 255.
                        # self.to_bin(pixel[ch]) :: Pasa a binario el valor del pixel en el canal.
                        # self.to_bin(pixel[ch])[:-1] :: El binario sin su bit menos significativo
                        # binary_secret_data[data_index] :: El bit de los datos secretos en la posición actual, el cual se reemplazará
                        
                        # Realiza la suma del binario del valor del pixel en el canal sin su bit menos significativo,
                        # con el bit actual de los datos secretos
                        # Este valor se le asigna al nuevo pixel
                        pixel[ch] = int(self.to_bin(pixel[ch])[:-1]+binary_secret_data[data_index],2)
                        
                        # Contador del bit actual de los datos secretos
                        data_index+=1
                    else:
                        break
        return self.image


    # Utiliza el Algoritmo LSB para obtener la información secreta
    def decode(self):
        # Cadena de bits (1 y 0), de los bits menos significativos de la imagen
        binary_data = ""
        # Recorre cada fila y pixel de la imagen
        for row in self.image:
            for pixel in row:
                # Obtiene cada canal del pixel actual
                r, g, b = self.to_bin(pixel)
                # Obtiene los bits menos significativos del binario en cada canal
                binary_data += r[-1]
                binary_data += g[-1]
                binary_data += b[-1]
                   
        # Lista de bytes, al dividir cadena de bits en valores de 8 bits
        all_bytes = [ binary_data[i: i+8] for i in range(0, len(binary_data), 8) ]

        # Borra el último byte de la cadena, cuando este no es de tamaño 8
        if len(all_bytes[-1])!=8:
            #print(f"\nlast byte: {all_bytes[-1]}\n")
            all_bytes = all_bytes[:-1]
        
        # Convierte los bytes a una cadena de caracteres
        decoded_data = ""
        for byte in all_bytes:
            decoded_data += chr(int(byte, 2))
        return decoded_data

    # Muestra la entropía de la imagen en un solo canal
    def show_entropy(self, img):
        height, width, ch = img.shape

        img_out_lsb = np.zeros((img.shape), dtype=np.uint8)
        for w in range(width):
            for h in range(height):
                img_out_lsb[h,w,:] = (img[h,w,:] & 0b00000001)*255
        return img_out_lsb[:,:,1]

    def resize_image(self, img, w=500, h=500):
        return cv2.resize(img, (w,h),interpolation = cv2.INTER_CUBIC)
     
    def ampliar_imagen(self, img, nombre):
        cv2.imshow(nombre, self.resize_image(img))


