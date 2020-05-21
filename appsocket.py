import socket
import select
import pickle


HEADERSIZE = 10


class AppSocket:
    def __init__(self, host, port):
        # Host
        self.host = host
        # Puerto
        self.port = port
        # Socket
        self.sk = None
        # Socket del destinatario
        self.othersk = None
        # Tipo: Cliente o Servidor
        self.type = None  
        
    # Inicia el peer actual como servidor
    def iniciar_servidor(self):
        try:
            self.sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sk.bind((self.host, self.port))
            self.sk.listen(5)
        except Exception as e:
            print("exception "+str(e))
            return f"Error al iniciar el servidor: {e}"
        return f"El servidor está a la espera de un cliente para realizar la conexión"

    # Método para que el servidor espere la conexión del cliente
    def esperar_conexiones(self):
        try:
            self.othersk, address = self.sk.accept()
            self.type = "Servidor"
        except Exception as e:
            print("exception "+e)
            return f"Error en la espera de conexiones: {e}"
        return f"Se ha iniciado el servidor en {self.host}:{self.port}"

    # Inicia el peer actual como cliente
    def iniciar_cliente(self):
        try:
            self.sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.othersk = self.sk
            self.othersk.connect((self.host,self.port))
            self.type = "Cliente"
        except Exception as e:
            print("exception "+str(e))
            return f"Error al conectarse al servidor: {e}"
        return f"Se ha conectado con el servidor {self.host}:{self.port}"
           
    # Envia un mensaje de longitud variable.
    def enviar_mensaje(self, objeto):
        # Utiliza pickle para serializar el mensaje
        msg = pickle.dumps(objeto)
        # Agrega encabezado con el tamaño del mensaje
        msg = bytes(f'{len(msg):<{HEADERSIZE}}',"utf-8")+msg
        # Envía el mensaje al otro peer
        self.othersk.send(msg)

    # Envía un mensaje clave, de un tamaño fijo de 2048 bits
    def enviar_mensaje_clave(self, msg):
        self.othersk.send(msg)

    # Escucha un mensaje clave, de un tamaño fijo de 2048 bits
    def escuchar_mensajes_clave(self):
        try:
            self.othersk.setblocking(0)
            ready = select.select([self.othersk], [], [], 0.1)
            if ready[0]:
                # Asigna los 2048 bits recibidos a la variable
                msg = self.othersk.recv(2048)
                return msg
        except:
            pass
        return None
    
    # Escucha un mensaje de longitud variable
    def escuchar_mensajes(self):
        self.othersk.setblocking(0)
        ready = select.select([self.othersk], [], [], 0.1)
        full_msg = b''
        new_msg = True
        msglen = 999999999
        if ready[0]:
            while True:
                # Recibe información cada 16 bytes
                msg = self.othersk.recv(16)
                # Verifica si son los primeros 16 bytes recibidos
                if new_msg:
                    # Obtiene la longitud del mensaje a partir del encabezado
                    msglen = str(msg[:HEADERSIZE].decode("utf-8")).strip(' ')
                    new_msg = False
                # Agrega los 16 bytes actuales al total del mensaje
                full_msg += msg
                # Verifica si se ha llegado al final del mensaje
                if str(len(full_msg)-HEADERSIZE) == msglen:
                    # Remueve el encabezado del mensaje
                    full_msg = full_msg[HEADERSIZE:]
                    # Obtiene el objeto original mediante pickle
                    full_msg = pickle.loads(full_msg)
                    break
        if full_msg!= b'':
            return full_msg
        else:
            return None









