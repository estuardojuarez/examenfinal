#C:\Users\rolan\AppData\Local\Programs\Python\Python38\Lib\site-packages

# import the necessary packages
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from imutils.video import VideoStream
import numpy as np
import imutils
import time
import cv2
import os
import sys
from timeit import default_timer as timer
from datetime import datetime 
# from mark2_jarvis import *
from playsound import playsound
import threading
import time
from datetime import datetime as dt
from mark2_jarvis import *
from limpiar import limpiar_pantalla
from tiva_comunication import *
import queue
from base_datos import *
#           -----------------           inicia programa voz        -----------------

hilo_tiva = threading.Thread(target = conectar, daemon =True)
hilo_tiva.start()
time.sleep(4.5)

#           -----------------   declaracion de variables principales    ------------
lista = []
lista_2=[]
transformacion = []

bandera = True
bandera2 = True
bandera3 = True
bandera4 = True
cont_rostros = 0

#           -----------------   deteccion de mascarilla     --------------------
def detect_and_predict_mask(frame, faceNet, maskNet):
	# grab the dimensions of the frame and then construct a blob
	# from it
	(h, w) = frame.shape[:2]
	blob = cv2.dnn.blobFromImage(frame, 1.0, (224, 224),(104.0, 177.0, 123.0))

	# pass the blob through the network and obtain the face detections
	faceNet.setInput(blob)
	detections = faceNet.forward()
	# print(detections.shape)

	# initialize our list of faces, their corresponding locations,
	# and the list of predictions from our face mask network
	faces = []
	locs = []
	preds = []

	# loop over the detections
	for i in range(0, detections.shape[2]):
		# extract the confidence (i.e., probability) associated with
		# the detection
		confidence = detections[0, 0, i, 2]

		# filter out weak detections by ensuring the confidence is
		# greater than the minimum confidence
		if confidence > 0.5:
			# compute the (x, y)-coordinates of the bounding box for
			# the object
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")

			# ensure the bounding boxes fall within the dimensions of
			# the frame
			(startX, startY) = (max(0, startX), max(0, startY))
			(endX, endY) = (min(w - 1, endX), min(h - 1, endY))

			# extract the face ROI, convert it from BGR to RGB channel
			# ordering, resize it to 224x224, and preprocess it
			face = frame[startY:endY, startX:endX]
			face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
			face = cv2.resize(face, (224, 224))
			face = img_to_array(face)
			face = preprocess_input(face)

			# add the face and bounding boxes to their respective
			# lists
			faces.append(face)
			locs.append((startX, startY, endX, endY))

	# only make a predictions if at least one face was detected
	if len(faces) > 0:
		# for faster inference we'll make batch predictions on *all*
		# faces at the same time rather than one-by-one predictions
		# in the above `for` loop
		faces = np.array(faces, dtype="float32")
		preds = maskNet.predict(faces, batch_size=32)
	else:
		# si ninguna cara es detectada, mantiene el valor 
		# de tiempo vacio hasta que se detecte        
		del lista[:]
		del lista_2[:]
	# return a 2-tuple of the face locations and their corresponding
	# locations
	return (locs, preds)

#       ------------    carga la deteccion de rostros y mascarillas      -----------
prototxtPath = r"face_detector\\deploy.prototxt"
weightsPath = r"face_detector\\res10_300x300_ssd_iter_140000.caffemodel"
faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)
maskNet = load_model("mask_detector.model")

#       ---------------     inicia el video para la captura     -----------------
print("Iniciando video...")
vs = VideoStream(src=0).start()





# loop over the frames from the video stream
while True:
	frame = vs.read()
	# detect faces in the frame and determine if they are wearing a
	# face mask or not
	(locs, preds) = detect_and_predict_mask(frame, faceNet, maskNet)
	auxFrame = frame.copy()
	# loop over the detected face locations and their corresponding
	# locations
	for (box, pred) in zip(locs, preds):
				
		# unpack the bounding box and predictions
		(startX, startY, endX, endY) = box
		(con_Mascarilla, sin_Mascarilla) = pred

		# determine the class label and color we'll use to draw
		# the bounding box and text

		if con_Mascarilla > sin_Mascarilla:
			label = "con Mascarilla"
			color = (255, 0, 0)
			valor_tiva = lista_tiv[0]            
			cv2.putText(frame, valor_tiva, (50, 150 ),cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)

			ingreso = time.time()
			lista.append(ingreso)
			resta = lista[-1] - lista[0]
			resta = round(resta,0)
			transformacion = valor_tiva.split(":")
			if resta == 0.0:
				fecha()
				analisis_con_mascarilla()	
			if resta == 5.0 :
				

				if float(transformacion[-1]) > 33:
					hilo4 = threading.Thread(target=analisis_sin_mascarilla_posterior)
					hilo4.start()
				else: 

					fecha()
					analisis_con_mascarilla_posterior()				
			else:
				fecha()
				del lista_2[:]

		


		else:
			ingreso = time.time()
			label = "sin Mascarilla"
			color = (0, 0, 255)
			lista_2.append(ingreso)
			resta2 = lista_2[-1] - lista_2[0]
			resta2 = round(resta2,0)
	

			if resta2 == 0.0:
				analisis_sin_mascarilla()  
				fecha()          
			elif resta2 == 3.0 :
				analisis_sin_mascarilla_posterior()
				fecha()		
			else:
				fecha()
				del lista[:]



		label = "{}".format(label)             
		cv2.putText(frame, label, (startX, startY - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
		cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)

	# show the output frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop



	if key == ord("q"):
		limpiar_pantalla()
		break


	# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
sys.exit()






