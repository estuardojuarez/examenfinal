import paho.mqtt.client as mqtt
import logging
import time
import os 

from brokerData import * #Informacion de la conexion
from datetime import datetime
import threading

import socket
import binascii
import sys

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

#(RESJ) Por este medio informo de mi entrega de mi examen final de proyectos de AIE
# y estare explicando a lo largo del cocumento la mayor cantidad posible de codigo
# se implemento el servidor TCP dentro de un broker de MQTT para poder realizar 
# transferencia de archivos y texto, aunemntando la complejidad agregando 
# encriptacion para los archivos de audio, como para los archivos de texto
# a lo largo de su viaje van encriptados utilizado SHA256, asi mismo se realiza
# una copia de encriptacion tanto de audios como de texto, esto se realizo meramente
# con fines de realizar pruebas debido a que trabaje solo, se me dificultaba mucho 
# implementar varios disporitivos de forma simultanea.



#Configuracion inicial de logging
logging.basicConfig(
    level = logging.INFO, 
    format = '[%(levelname)s] (%(threadName)-10s) %(message)s'
    )


def on_connect(client, userdata, rc):#Callback que se ejecuta cuando nos conectamos al broker
    logging.info("Conectado al broker")


#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
                        #             encriptacion                  #
#se implemento una llave para poder encriptar dichos la cual utiliza un algoritmo para poder 
#cambiar cualquier tipo de caracter, es decir se puede utilizar dicho algoritmo
#ya sea para encriptar texto, audio, imagener, cualquier tipo de dato logico puede ser encriptado
#lo cual es bastante conveniente debido a se enviaran paquetes por medio del protocolo TCP 
#del modelo OSI

def encrypt(key, filename):         #(RESJ) necesita su password y un archivo de cualquier tipo
	outputFile = "(encriptado)"+filename #le otorga un nombre que sera utilizado al finalizar
	filesize = str(os.path.getsize(filename)).zfill(16)
	IV = Random.new().read(16)  #obtiene caracateres aleatorios
	encryptor = AES.new(key, AES.MODE_CBC, IV)
	with open(filename, 'rb') as infile:
		with open(outputFile, 'wb') as outfile:
			outfile.write(filesize.encode('utf-8'))
			outfile.write(IV)			
			while True:
				chunk = infile.read(BUFFER_SIZE)	#hace codificacion con un buffer de 64k		
				if len(chunk) == 0:                                         
					break
				elif len(chunk) % 16 != 0:
					chunk += b' ' * (16 - (len(chunk) % 16))    #una vez finalizado el proceso de
				outfile.write(encryptor.encrypt(chunk))     #cambio, genera el nuevo archivo
 
 
#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
                        #             encriptacion                  #
# proceso inverso de la encriptacion aplicando la misma llave(password), regresa a su forma 
# original una vez haya llegado a su destino, lo cual otorga mayor seguridad al momento de
# transferir archivos o documentos de suma importancia se le otorga un nombre caracteristico
#para que el archivo pueda ser comparado con el original
    
def decrypt(key, filename):
	outputFile = filename[11:]	
	with open(filename, 'rb') as infile:
		filesize = int(infile.read(16))
		IV = infile.read(16)
		decryptor = AES.new(key, AES.MODE_CBC, IV)
		with open("desencriptado"+outputFile, 'wb') as outfile:
			while True:
				chunk = infile.read(BUFFER_SIZE)
				if len(chunk) == 0:
					break
				outfile.write(decryptor.decrypt(chunk))
			outfile.truncate(filesize)







                        #       implementacion de hilos para la seccion de alive  #
#primer hilo de cliente - servidor
#una vez se conecta el usuario este hilo debe de 
#hiciar su contedo de mandar una respuesta cada 2 segundos al servidor
def alive_clock():
    contador = 0
    separador = bytes('$', "ascii")
    cuenta_local = bytes(SENDER, "ascii")
    trama = COMMAND_FTR + separador + cuenta_local
    while contador<4:
        time.sleep(1)
        contador+=1
        
        logging.info("Ha llegado el mensaje al topic: "+contador)    
        
        
hilo1 = threading.Thread(target=alive_clock,daemon = False)
hilo1.start()
#se coloca deamon = False para que el proceso muera con el target    
    






#Callback que se ejecuta cuando llega un mensaje al topic suscrito
def on_message(client, userdata, msg):
    #Se muestra en pantalla informacion que ha llegado
    #logging.info("Ha llegado el mensaje al topic: " + str(msg.topic))
    recibido = msg.payload
    #logging.info("El contenido del mensaje es: " + str(recibido))
    separador = bytes('$', "ascii")
    #for i in range(0,5):    
    separacion = recibido.split(separador,5) #realiza la separacion de cacteres, solo 5 espacios maximo
    #convierte todo a string
    
    
#---------------------------------------------------------------------           
#---------------------------------------------------------------------           
#----- mensajes encriptados a salas y usuarios (RESJ)----------------            
#---------------------------------------------------------------------            
#---------------------------------------------------------------------  
# todos los mensajes se mandan de manera encriptada utilizando las funciones
# decrypt() y encrypt, se crean archivos de texto para que se pueda ver la valides
# de la encriptacion dicha encriptacion esta dividida en 5 etapas:
#     1- almacenamiento de texto
#     2- encriptacion
#     3- envio al servidor
#     4- envio del servidor al cliente
#     5- recepcion del archivo encriptado
#     6- decodificacion aplicando el password "patos"


    
    if separacion[0].decode("utf-8") == MI_SALA:                #MI_SALA: mensajes de mi sala
                                                                #si un mensaje no va dirijido a èl
        recepcion= 'texto_encriptado_desde_el_servidor.txt'     #no hace ninguna accion de recepcion
        with open(recepcion, "wb") as f:                        #cada usuario debe modificar su sender
            f.write(separacion[1])                              #en el archivo brokerData.py        
        f.close()
        hasher = SHA256.new(password.encode('utf-8'))
        decrypt(hasher.digest(), recepcion)                
        recepcion= 'desencriptadoptado_desde_el_servidor.txt'    
        with open(recepcion, "r") as f:
            datos = f.read()
            print("Texto de sala "+separacion[0].decode("utf-8") +" : "+datos)
        f.close()            

    elif separacion[0].decode("utf-8") == SENDER:               #SENDER(texto): es el que manda el mensaje
                                                                #si un mensaje no va dirijido a èl
        recepcion= 'texto_encriptado_desde_el_servidor.txt'     #no hace ninguna accion de recepcion
        with open(recepcion, "wb") as f:                        #cada usuario debe modificar su sender
            f.write(separacion[1])                              #en el archivo brokerData.py        
        f.close()
        hasher = SHA256.new(password.encode('utf-8'))
        decrypt(hasher.digest(), recepcion)    
        recepcion= 'desencriptadoptado_desde_el_servidor.txt'    
        with open(recepcion, "r") as f:
            datos = f.read()
            print("Texto de sala "+separacion[0].decode("utf-8") +" : "+datos)
        f.close()                
#--------------------------------------------------------------------- 
#--------------------------------------------------------------------- 
#---------------------------------------------------------------------             
#--------------------------------------------------------------------- 
#--------------------------------------------------------------------- 
#--------------------------------------------------------------------- 
#--------------------------------------------------------------------- 
#---------------------  manejo de la recepcion de audio(RESJ) ------------- 
# de la misma forma que con el texto, se realizo la encriptacion de el archivo.wav
# para lugo poder ser transmitido, recibido y decodificado utilizando la misma 
# clave patos, solo si los archivos van dirigidos para mi los puedo recibir, de lo contrario
# el usuario correspondiente con su SENDER recibira el archivo
    elif separacion[0] == binascii.unhexlify("03") and separacion[1].decode("utf-8") == SENDER:
        
        s = socket.socket(socket.AF_INET,   socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        print("[+] Connected with Server")
        f = open("file_received_encriptado.wav", "wb")
        while True:
            data = s.recv(BUFFER_SIZE)
            f.write(data)
            print(f)
            
            if not data:
                break
        f.close()
        print("[+] Download complete!")
        s.close()
        print("[-] Client disconnected")
        recepcion= 'file_received_encriptado.wav'   
        hasher = SHA256.new(password.encode('utf-8'))
        decrypt(hasher.digest(), recepcion)                
        os.system('aplay desencriptadoed_encriptado.wav')      


#--------------------------------------------------------------------- 
#--------------------------------------------------------------------- 
#--------------------------------------------------------------------- 
#--------------------------------------------------------------------- 
#--------------------------------------------------------------------- 
#--------------------------------------------------------------------- 
#--------------------------------------------------------------------- 
#--------------------codificador para las salas de audio--------------             
#--------------------------------------------------------------------- 
    #si se manda un File request, se obtiene su codigo identificador y la sala a la que se 
    #enviara, si la sala es mi sala a la que yo pertenezco yo recibo el mensaje, de lo contrario
    #se enviara de forma de broadcast para que solo a quien corresponda sea capaz de recibir 
    #el mensaje.
    elif separacion[0] == binascii.unhexlify("03") and separacion[1].decode("utf-8") == MI_SALA:
        s = socket.socket(socket.AF_INET,   socket.SOCK_STREAM) #ipv4 tcp
        s.connect((HOST, PORT)) #se conecta al puerto y host
        print("[+] Connected with Server")
        f = open("file_received__salas_encriptado.wav", "wb")
        while True:#mientras existan datos seguira escribiendo en el archivo
            data = s.recv(BUFFER_SIZE)
            f.write(data)
            print(f)            
            if not data:
                break
        f.close()#se cierran las interfaces de comunicacion de TCP
        print("[+] Download complete!")
        s.close()
        print("[-] Client disconnected")
        
        #una vez finalizado el proceso se  vuelve a abrir el archivo para
        #porderlo decodificar
        recepcion= 'file_received__salas_encriptado.wav'   
        hasher = SHA256.new(password.encode('utf-8'))
        decrypt(hasher.digest(), recepcion)                
        os.system('aplay desencriptadoed_encriptado.wav')      

 #Y se almacena en el log 
    logCommand = 'echo "(' + str(msg.topic) + ') -> ' + str(msg.payload) + '" >> ' + LOG_FILENAME
    os.system(logCommand)


client = mqtt.Client(clean_session=True) #Nueva instancia de cliente
client.on_connect = on_connect #Se configura la funcion "Handler" cuando suceda la conexion
client.on_message = on_message #Se configura la funcion "Handler" que se activa al llegar un mensaje a un topic subscrito
client.username_pw_set(MQTT_USER, MQTT_PASS) #Credenciales requeridas por el broker
client.connect(host=MQTT_HOST, port = MQTT_PORT) #Conectar al servidor remoto


#simplificacion para realizar publicaciones en topics
def publishData(topicRoot, topicGrupo, topcUsuario, value, qos = 0, retain = True):
    topic = topicRoot + "/" + topicGrupo + "/" + topcUsuario
    client.publish(topic, value, qos, retain)

#Nos conectaremos a distintos topics:
qos = 2

# #Subscripcion simple con tupla (topic,qos)
client.subscribe((comandos, qos))
salas = 'salas.txt'
f = open(salas)
with open(salas, "r") as f:
    datos = f.read()
    cambi = list(datos.split("\n"))
    del cambi[-1]
    for i in cambi:
        separacion= list(i.split("S"))
        #print(separacion[0]+"S"+ separacion[1])
        client.subscribe(("salas/"+separacion[0]+"/S"+separacion[1], qos))    
        # el archivo de texto tiene el formato 201112345

    
usuario = 'usuarios.txt'
f = open(usuario)
with open(usuario, "r") as f:
    datos = f.read()
    cambi = list(datos.split("\n"))
    for i in cambi:
        client.subscribe(("usuarios/02/"+i, qos))
#tiene el formato 14S02

#Iniciamos el thread (implementado en paho-mqtt) para estar atentos a mensajes en los topics subscritos
client.loop_start()

#El thread de MQTT queda en el fondo, mientras en el main loop hacemos otra cosa

try:
    while True:     
        print("loading...")   
        time.sleep(1)            
        ingrese = input('''
                        
NOTA: se sugiere como ejemplo utilizar mis datos para poder observar 
como se envian y reciben los mensajes

usuario : 200819010
Grupo: 02

1-Enviar texto
    1.1 Enviar a usuario
    1.2 Enviar a sala
2-Enviar mensaje de voz
    2.1 Enviar a usuario
    2.2 Enviar a sala
    
3-Para salir

ingrese su opcion: ''')
        
        if ingrese == "1.1":                                
#       -------------       texto a una persona (usuarios/15/201532658  )     ----------------
            Nogrupo = input("ingrese No. grupo: ")      #ingresa numero de grupo
            NoID = input("client ID(destino): ")       #ingresa numero de carnet
            texto = input("texto a enviar: ")       #cantidad de segundos de duracion del audio
            topic = "usuarios"
            
            f = open('texto_usuarios.txt','w')
            f.write(texto)
            f.close()
            #se abre el archivo de audio y se une en un raw para ser enviado por completo
            #inicio del proceso de encriptacion
            archivotex = 'texto_usuarios.txt'
            separador = bytes('$', "ascii")
            usuario_final = bytes(NoID, "ascii")
            hasher = SHA256.new(password.encode('utf-8'))
            encrypt(hasher.digest(), archivotex)
            archi_encri ="(encriptado)texto_usuarios.txt"
            with open(archi_encri, "rb") as f:
                datos = f.read()  
                trama = usuario_final+separador + datos 
                publishData(topic,Nogrupo, NoID,trama )  
            f.close()
            


#---------------------------------------------------------------------           
#--------------------------------------------------------------------- 
#---------------------------------------------------------------------           
#--------------------------------------------------------------------- 
#---------------------------------------------------------------------           
#--------------------------------------------------------------------- 
#---------------------------------------------------------------------           
#--------------------------------------------------------------------- 
#---------------------------------------------------------------------          

        elif ingrese == "1.2":
 #       -------------       texto a una sala (salas/15/15S03   )     ----------------
            Nogrupo = input("ingrese No. grupo: ")      #ingresa numero de grupo
            NoID = input("Sala ID(destino): ")       #ingresa numero de carnet
            texto = input("texto a enviar: ")       #cantidad de segundos de duracion del audio
            topic = "salas"


            f = open('texto_salas.txt','w')
            f.write(texto)
            f.close()
            #se abre el archivo de audio y se une en un raw para ser enviado por completo
            #inicio del proceso de encriptacion
            archivotex = 'texto_salas.txt'
            separador = bytes('$', "ascii")
            grupos = bytes("s", "ascii")
            grupo_final = bytes(Nogrupo, "ascii")
            usuario_final = bytes(NoID, "ascii")
            hasher = SHA256.new(password.encode('utf-8'))
            encrypt(hasher.digest(), archivotex)
            archi_encri ="(encriptado)texto_salas.txt"
            with open(archi_encri, "rb") as f:
                datos = f.read()  
                trama12 = grupo_final+usuario_final+separador+datos
                publishData(topic,Nogrupo, NoID,trama12 )  
            f.close()



#--------------------------------------------------------------------- 
#--------------------------------------------------------------------- 
#---------------------------------------------------------------------             
#---------------------------------------------------------------------           
#---------------------------------------------------------------------           
#------------------------seccion de audio  a usuario------------------            
#---------------------------------------------------------------------            
#---------------------------------------------------------------------            
        elif ingrese == "2.1":            
            #       -------------       grabar audio a una persona (audio/20/202012345 )     ----------------
            Nogrupo = input("ingrese No. grupo: ")      #ingresa numero de grupo
            NoID = input("client ID(destino): ")       #ingresa numero de carnet
            tiempo1 = input("segundos del audio: ")       #cantidad de segundos de duracion del audio
            topic = "usuarios"
            
            #se graba el audio
            print("     ")
            print("se enviara a: audio/"+Nogrupo+'/'+NoID)
            print('Comenzando grabacion')
            grab = os.system('arecord -d '+tiempo1+' -f U8 -r 8000 200819010_grupo_02.wav ')                
            print('grabacion finalizada')    
            print("     ")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
            #cambio de valores a bytes para ser mandados
            FTR = b'\x03'
            bit_grupo = bytes(Nogrupo, "ascii")
            bit_usuario = bytes(NoID, "ascii")
            separador = bytes('$', "ascii")
            audio_file = '200819010_grupo_02.wav'
            tamanio = os.stat(audio_file).st_size
            bit_tama = bytes(str(tamanio), "ascii")
            identi = bytes('audio', "ascii")
            emisor = bytes(SENDER, "ascii")
            #se abre el archivo de audio y se une en un raw para ser enviado por completo
            with open(audio_file, "rb") as f:
                print("[+] Sending file...")
                datos = f.read()    
                Trama11 = FTR+separador+bit_usuario+separador+bit_tama
            publishData(topic,Nogrupo, NoID,Trama11 )
#envia los archivos por TCP
            s.bind((HOST, PORT))
            s.listen(1)
            print("Listening ...")
            while True:
                conn, addr = s.accept()
                logging.info("[+] Client connected: ")
                f_send = "200819010_grupo_02.wav"                
                hasher = SHA256.new(password.encode('utf-8'))
                encrypt(hasher.digest(), f_send)  
                auidio_encri = "(encriptado)200819010_grupo_02.wav"                          
                
                with open(auidio_encri, "rb") as f:
                    data = f.read()
                    conn.sendall(data)
                break
            f.close()
            s.close() 
            conn.close() 
            

            
#---------------------------------------------------------------------           
#---------------------------------------------------------------------           
#------------------------seccion de audio  a una sala-----------------            
#---------------se dejo habilitada para la entrega final -------------            
#---------------------------------------------------------------------                        
            
        elif ingrese == "2.2":

#-------------       grabar audio a una sala (audio/20/15S03 )  ----------------
           
            Nogrupo = input("ingrese No. grupo: ")      #ingresa numero de grupo
            NoID = input("sala ID(destino): ")       #ingresa numero de carnet
            tiempo1 = input("segundos del audio: ")       #cantidad de segundos de duracion del audio
            topic = "salas"

            #se graba el audio
            print("     ")
            print("se enviara a: audio/"+Nogrupo+'/'+NoID)
            print('Comenzando grabacion')
            grab = os.system('arecord -d '+tiempo1+' -f U8 -r 8000 200819010_sala_grupo_02.wav ')                
            print('grabacion finalizada')    
            print("     ")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
            #cambio de valores a bytes para ser mandados
            FTR = b'\x03'
            bit_grupo = bytes(Nogrupo, "ascii")
            bit_usuario = bytes(NoID, "ascii")
            separador = bytes('$', "ascii")
            audio_file = '200819010_sala_grupo_02.wav'
            tamanio = os.stat(audio_file).st_size
            bit_tama = bytes(str(tamanio), "ascii")
            identi = bytes('audio', "ascii")
            emisor = bytes(SENDER, "ascii")
            #se abre el archivo de audio y se une en un raw para ser enviado por completo
            with open(audio_file, "rb") as f:
                print("[+] Sending file...")
                datos = f.read()    
                Trama11 = FTR+separador+bit_grupo+bit_usuario+separador+bit_tama
                print(Trama11)
            publishData(topic,Nogrupo, NoID,Trama11 )
#envia los archivos por TCP
            s.bind((HOST, PORT))
            s.listen(1)
            print("Listening ...")
            while True:
                conn, addr = s.accept()
                logging.info("[+] Client connected: ")
                f_send = "200819010_sala_grupo_02.wav"                
                hasher = SHA256.new(password.encode('utf-8'))
                encrypt(hasher.digest(), f_send)  
                auidio_encri = "(encriptado)200819010_sala_grupo_02.wav"                                          
                with open(auidio_encri, "rb") as f:
                    data = f.read()
                    conn.sendall(data)
                break
            f.close()
            s.close() 
            conn.close() 





        elif ingrese == "3":
            sys.exit(0)




        
        

except KeyboardInterrupt:
    logging.warning("Desconectando del broker...")
finally:
    client.loop_stop() #Se mata el hilo que verifica los topics en el fondo
    client.disconnect() #Se desconecta del broker
    logging.info("Desconectado del broker. Saliendo...")

