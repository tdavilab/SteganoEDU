from appsocket import AppSocket
from algoritmos_seguridad import AESCifrador
from algoritmos_seguridad import AppRSA
from algoritmos_seguridad import AESDescifrador
import time
from stegano_code import Stegano
import numpy as np
import time as t
import cv2

class Facade:
    __instance = None
    @staticmethod 
    def getInstance():
      """ Static access method. """
      if Facade.__instance == None:
         Facade()
      return Facade.__instance
    def __init__(self):
      """ Virtually private constructor. """
      if Facade.__instance != None:
         raise Exception("This class is a singleton!")
      else:
         Facade.__instance = self
         self.cifrador = AESCifrador()
         self.descifrador = AESDescifrador()
         self.apprsa = AppRSA()    
         self.encoder = Stegano()
         self.decoder = Stegano()
         self.app = None
         self.gui = None

    def registrar_gui(self, gui):
        if self.gui == None:
            self.gui = gui

    def crear_socket(self, host, port):
        self.app = AppSocket(host, port)

    def iniciar_cliente(self):
        validacion = self.app.iniciar_cliente()
        t.sleep(4)
        # ALGORITMO RSA
        print("[+] Creando Claves RSA...")
        # Genera las claves pública y privada locales
        
        t1 = t.time()
        
        clave_publica, clave_privada = self.apprsa.generar_claves()
        print("[+] Claves RSA Generadas...")
        
        t2 = t.time() - t1
        print('[+] Descifrado Finalizado.' )
        print('     [*] Tiempo de ejecución Claves RSA: ', t2, 's')
        
        # Intercambio de claves. Envía mi clave pública.
        self.enviar_clave_publica()
        print("[+] Claves RSA Intercambiadas...")
        return validacion

    def esperar_conexiones(self):
        validacion = self.app.esperar_conexiones()
        return validacion
        
    def iniciar_servidor(self):
        validacion = self.app.iniciar_servidor()
        
               
        # ALGORITMO RSA
        #print("[+] Creando Claves RSA...")
        #print("     [*] Precaución: No conectarse al servidor hasta que se generen las claves")
        
        #t1 = t.time()
        
        # Genera las claves pública y privada locales
        #clave_publica, clave_privada = self.apprsa.generar_claves()
        #print("[+] Claves RSA Generadas...")
        
        print("     [*] Conectese al servidor con la aplicación del Cliente")
        
        #t2 = t.time() - t1
        #print('     [*] Tiempo de ejecución Claves RSA: ', t2, 's')
        
        return validacion
            
    # Permite escuhar si se ha recibido un mensaje del otro peer.
    # Este método es llamado todo el tiempo desde la interfaz para verificar el socket.
    def escuchar_mensajes(self):
        #print("Metodo Escuchar Msgs...")
        if not self.cifrador.recibir_mensaje:
            # Se usa para intercambiar claves, se escucha siempre por información de tamaño 2048 bytes
            msg_bytes = self.app.escuchar_mensajes_clave()
        else:
            # Se usa para recibir información de tamaño dinámico, en este caso la imagen
            msg_bytes = self.app.escuchar_mensajes()

        if msg_bytes != None:
            if self.verificar_clave_recibida(msg_bytes):
                # Recibio la clave publica del otro
                self.apprsa.otra_clave_publica = msg_bytes
                #self.gui.mostrar_clave_publica_recibida(msg_bytes)
                print("[*] He recibido la clave pública del otro...")
                # Si yo no he intercambiado mi clave, se la envío al otro
                if not self.apprsa.intercambio:
                    print("[+] Creando Claves RSA...")
                    t1 = t.time()
                    # Genera las claves pública y privada locales
                    clave_publica, clave_privada = self.apprsa.generar_claves()
                    t2 = t.time() - t1
                    print('     [*] Tiempo de ejecución Claves RSA: ', t2, 's')
                    
                    self.enviar_clave_publica() 
                    print("[+] Claves RSA Intercambiadas...")
                    
                self.cifrador.recibir_mensaje = True
            else:
                # Recibio el archivo cifrado
                print("[*]Recibio archivo cifrado")
                
                # Convierte la string recibida a un arreglo de numpy
                nparr = np.fromstring(msg_bytes, np.uint8)
                # Decodifica el arreglo de numpy como una imagen cv2
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                # Guarda la imagen recibida en el decoder de esteganografia
                self.decoder.receive_image(img)
                # Obtiene las miniaturas de la imagen recibida
                #img, img_e = self.obtener_miniaturas(self.decoder)
                # Muestra las miniaturas en la interfaz
                #self.gui.mostrar_imagenes(img, img_e, 'recibida')
        else:
            #self.apprsa.intercambio = False
            pass

    def verificar_clave_recibida(self, msg):
        if "begin public key" in str(msg.lower()):
            return True
        return False
        
    # Genera la clave pública y privada
    def generar_claves(self):
        print("\n[*] Generando Claves...\n")
        clave_publica, clave_privada = self.apprsa.generar_claves()
        print("[*] Claves pública y privada generadas")
        return clave_publica, clave_privada    
        
    # Envía mi clave pública al destinatario
    def enviar_clave_publica(self):
        self.app.enviar_mensaje_clave(self.apprsa.clave_publica)
        self.apprsa.intercambio = True
    
    # Envía la nueva imagen codificada al otro peer
    def enviar_mensaje(self):
        try:
            # String de la matriz de la nueva imagen almacenada en memoria
            img_str = cv2.imencode('.png', self.encoder.newimage)[1].tostring()
            self.app.enviar_mensaje(img_str)
            time.sleep(.1)
        except Exception as e:
            print(e)
            return f"Se ha presentado un error {e}"
        return "El archivo se ha enviado correctamente"

    
            
    ##########################################
    

    def abrir_archivo(self, ruta):        
        with open(ruta, 'rb') as txt:
            self.cifrador.plain_text_Bytes = txt.read()
            self.cifrador.plain_text = str(self.cifrador.plain_text_Bytes)
        return len(self.cifrador.plain_text_Bytes)

    def abrir_imagen(self, ruta):       
        self.encoder.read_image(ruta)                
        return self.encoder.n_bytes

    def guardar_archivo(self, ruta):
       with open(ruta, 'wb') as txt:
            txt.write(self.descifrador.texto_descifrado)
    
    def guardar_imagen(self, ruta):
        cv2.imwrite(ruta, self.encoder.newimage)
        
    def obtener_miniaturas(self, steg):
        img = steg.resize_image(steg.image, 120, 120)
        img_e = steg.resize_image(steg.image_entropy, 120, 120)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
        return img, img_e

    def ampliar_imagen(self, name):
        if name == 'original':
            img = self.encoder.image
        elif name == 'original_entropia':
            img = self.encoder.image_entropy
        elif name == 'nueva':
            img = self.encoder.newimage
        elif name == 'nueva_entropia':
            img = self.encoder.newimage_entropy
        elif name == 'recibida':
            img = self.decoder.image
        elif name == 'recibida_entropia':
            img = self.decoder.image_entropy
        self.encoder.ampliar_imagen(img, name)
                     
    def check_size(self):
        return self.encoder.check_size(self.cifrador.plain_text_Bytes)
                     
    def cifrar(self):
        print("[+] Ejecutando Algoritmo de Cifrado...")
        # Captura tiempo inicial
        t1 = t.time()
               
        # CLAVE DE SESIÓN 
        # Obtiene la clave de sesion de la interfaz
        clave = self.gui.obtener_clave()
        
        t1_hash = t.time()
        
        # Hashea la clave de sesión
        self.cifrador.hashear_clave(clave)
        
        t2_hash = t.time() - t1_hash
        print('[+] Hash Finalizado.' )
        print('     [*] Tiempo de ejecución Hash: ', t2_hash, 's')
        
        # CADENA ALEATORIA
        # Agrega la cadena aleatoria (relleno) al texto
        full_txt_relleno, print_str = self.encoder.agregar_relleno(self.cifrador.plain_text_Bytes)


        t1_aes = t.time()

        # ALGORITMO AES CBC
        print("[+] Ejecutando AES CBC...")
        # Se le envía al cifrador
        self.cifrador.plain_text_Bytes = full_txt_relleno
        # Cifra el texto con el relleno
        texto_cifrado, iv = self.cifrador.cifrar_archivo()
        
        t2_aes = t.time() - t1_aes
        print('[+] Cifrado AES Finalizado.' )
        print('     [*] Tiempo de ejecución AES: ', t2_aes, 's')
        
        # CIFRA INFORMACIÓN CON LA CLAVE PÚBLICA RSA
        # Cifra la clave de sesión cs con la clave pública del destinatario
        cs_c = self.apprsa.cifrar_clave(self.cifrador.clave_sesion)
        # Cifra la última subclave iv con la clave pública del destinatario
        iv_c = self.apprsa.cifrar_clave(iv)


        # Contenido que se guardará en la imagen (Clave Pública + Clave Sesión + Última Subclave Cifrada + Texto Cifrado)
        full_content = cs_c + iv_c + texto_cifrado


        t1_estegano = t.time()

        # ALGORITMO ESTEGANOGRAFÍA
        print("[+] Ejecutando Algotirmo Esteganografía...")
        # Codifica el contenido en la imagen
        encoded_image = self.encoder.encode(full_content)

        t2_estegano = t.time() - t1_estegano
        print('[+] Cifrado Esteganografia Finalizado.' )
        print('     [*] Tiempo de ejecución Cifrado Esteganografía: ', t2_estegano, 's')
               
        # Tiempo de ejecución
        t2 = t.time() - t1
        print('[+] Cifrado Finalizado.' )
        print('     [*] Tiempo de ejecución: ', t2, 's')
               
        # Asigna variables para visualizar la imágen generada y su entropía
        self.encoder.newimage = encoded_image
        self.encoder.newimage_entropy = self.encoder.show_entropy(self.encoder.newimage)
        
        # Genera las miniaturas de la nueva imágen y su entropía
        newimg = self.encoder.resize_image(encoded_image, 120, 120)
        newimg_e = self.encoder.resize_image(self.encoder.newimage_entropy,120,120)
        newimg = cv2.cvtColor(newimg, cv2.COLOR_BGR2RGB) 
        
        # Imprime información acerca del número de bytes de las variables utilizadas
        print("\n[+] Información General")
        print(print_str)
        print(f"    [*] Longitud Clave Pública: {len(self.apprsa.otra_clave_publica)}")
        print(f"    [*] Longitud Clave Sesión Cifrada (cs_c): {len(cs_c)}")
        print(f"    [*] Longitud Última Subclave Cifrada (iv_c): {len(iv_c)}")
        print(f"    [*] Longitud del contenido: (clave_publica+cs_c+iv_c+texto_cifrado) = {len(full_content)}")
        print(f"    [*] Tamaño de la imagen: {self.encoder.n_bytes}")
        

        return newimg, newimg_e

    def descifrar(self):
        print("[+] Ejecutando Algoritmo de Descifrado...")
        decoder = self.decoder
        # Captura tiempo inicial
        t1 = t.time()
        
        t1_estegano = t.time()
        
        # ALGORITMO ESTEGANOGRAFÍA
        print("[+] Ejecutando Algotirmo Esteganografía...")
        # Obtiene el contenido en la imagen
        decoded_data = decoder.decode()
        decoded_data_bytes = decoded_data.encode("latin1")
        

        t2_estegano = t.time() - t1_estegano
        print('[+] Descifrado Esteganografia Finalizado.' )
        print('     [*] Tiempo de ejecución Descifrado Esteganografía: ', t2_estegano, 's')

        with open('zdecoded_data.txt','w') as f:
            f.write(str(decoded_data_bytes))

        # OBTIENE LAS VARIABLES ORIGINALES
        print("[+] Obteniendo las Variables Originales...")

        # Obtiene clave de sesión cifrada
        cs_c = decoded_data_bytes[:256]
        # Obtiene última subclave cifrada
        iv_c = decoded_data_bytes[256:512]

        # Valor para obtener el limite del texto cifrado original. 
        sum_mod = len(decoded_data_bytes)%16
        # Obtiene texto cifrado
        texto_cifrado = decoded_data_bytes[512:len(decoded_data_bytes)-sum_mod]



        # DESCIFRA INFORMACIÓN CON LA CLAVE PRIVADA RSA
        # Descifra la clave de sesión cifrada
        cs_d = self.apprsa.descifrar_clave(cs_c)
        # Descifra la última subclave cifrada
        iv_d = self.apprsa.descifrar_clave(iv_c)

        t1_aes = t.time()

        # ALGORITMO AES CBC
        print("[+] Ejecutando AES CBC...")
        # Asigna las variables en el descifrador
        self.descifrador.clave_sesion_descifrada = cs_d
        self.descifrador.iv_descifrado = iv_d
        self.descifrador.texto_cifrado = texto_cifrado
        # Ejecuta el algoritmo de descifrado AES CBC y obtiene el texto plano original
        texto_descifrado = self.descifrador.descifrar_archivo()
        # Remueve la cadena de texto aleatoria del texto plano
        self.descifrador.texto_descifrado = texto_descifrado.split(b"====")[0]

        t2_aes = t.time() - t1_aes
        print('[+] Descrifrado AES Finalizado.' )
        print('     [*] Tiempo de ejecución Descifrado AES: ', t2_aes, 's')


        # Tiempo de ejecución
        t2 = t.time() - t1
        print('[+] Descifrado Finalizado.' )
        print('     [*] Tiempo de ejecución: ', t2, 's')

        # Imprime información acerca del número de bytes de las variables utilizadas
        print("\n[+] Información Recibida")
        print(f"    [*] Tamaño de la imagen: {len(decoded_data_bytes)}")
        print(f"    [*] Texto Cifrado: {len(texto_cifrado)}")
        print(f"    [*] Longitud Clave Sesión Cifrada: {len(cs_c)}")
        print(f"    [*] Longitud Última Subclave Cifrada: {len(iv_c)}")
        







