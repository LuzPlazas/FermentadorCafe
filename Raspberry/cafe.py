import RPi.GPIO as GPIO #Librer?a para controlar GPIO
#sudo apt-get install python3-serial  ó pip install serial
import serial
import os
#import Arduino~
#sudo apt-get  install python3-pandas
import pandas as pd
#sudo apt-get install csv python3  ó  sudo pip3 install python-csv
import csv
#sudo apt-get  install python3-numpy
import numpy as np
from time import strftime, localtime, asctime

from datetime import time as tm
from datetime import datetime, date, timedelta
#	sudo apt install python3-picamera
                #from picamera import PiCamera
from time import sleep
arduino = serial.Serial('/dev/ttyUSB0',19200)
#arduino = serial.Serial('/dev/ttyUSB0',9600) 
arduino.setDTR(False)
sleep(1)
arduino.flushInput()
arduino.setDTR(True)
nombreA=asctime(localtime())
  
GPIO.setmode(GPIO.BCM) #Simplemente nos sirve para usar n?meros de pin de placa y no del procesador
GPIO.setwarnings(False) #Con esto impedimos que nos aparezcan warnings que en este caso no ser?n importantes
led = 21 #Variable donde ponemos el pin que usaremos para el LED
GPIO.setup(led, GPIO.OUT) #Configuramos el pin 21 (led) como salida
GPIO.output(led,0) #Apagado el LED
led2 = 16 #Variable donde ponemos el pin que usaremos para el LED
GPIO.setup(led2, GPIO.OUT) #Configuramos el pin 16 (led2) como salida
GPIO.output(led2,0) #Apagado el LED

PHprom = 0
cont = 0
maxCO2 = 0
ALprom = 0
DT1prom = 0
DT2prom = 0
TDSprom = 0
minT2 = 100
DCO2prom = 0
DALprom = 0
Samples = 1440
flagS = 10
umbralCal = 7.5
dataCalprom = 0
flagcalprom = 0

TD = []
C= []
A = []
P = []
t1 = []
t2 = []
t = []
Q = []
fcalidad = []
contC =[]
derivT1 = []
derivCO2 = []
derivAL = []
derivT2 = []
calp = []
dataD = {}
vmedianaPH = []
vDCO2prom = []
vDALprom = []
vDT1prom = []
vDT2prom = []
vdesvTDS = []

vPHprom = []
vmaxCO2 = []
vALprom = []

vTDSprom = []
vminT2 = []


def promedio(datop,dato,c):
    datop = (datop*(c-1)+dato)/c;
    print("Prom: "+str(datop))
    return datop
def maximo(maxdato,dato):
    if maxdato < dato:
        maxdato = dato
    print("Max: "+str(maxdato))
    return maxdato
def minimo(mindato,dato):
    if mindato > dato:
        mindato = dato
    print("Min: "+str(mindato))
    return mindato
def derivada(deriv,S,c):
    deltaD=0
    if c == 1:
        #datoprev = S.pop(c-1)
        deriv.append(0)
    elif c > 1:
        deltaD = S[c-1]-S[c-2]
        #datoprev = dato
        deriv.append(deltaD)
    print("derivada: "+str(deltaD))
    return deltaD
def calcPerfil1(v1,v2,v3,v4,v5,v6,v7):#aroma
    b = 7.2010438424
    a1 = 0.0001870258
    a2 = -0.0002191831
    a3 = -6.98251646
    a4 = 3.30947832
    a5 = -109.077613
    a6 = -92.8057011
    a7 = -0.003117922
    calcP = b+a1*v1+a2*v2+a3*v3+a4*v4+a5*v5+a6*v6+a7*v7
    return calcP
def calcPerfil2(v1,v2,v3,v4,v5):#sabor
    b = 7.5329376768
    a1 = 0.0002070077
    a2 = 0.0001116647
    a3 = -0.0013390289
    a4 = -0.0008735337
    a5 = -24.7612518
    calcP = b+a1*v1+a2*v2+a3*v3+a4*v4+a5*v5
    return calcP
def calcPerfil3(v1,v2,v3,v4,v5,v6,v7):
    b = 4.64572458
    a1 = 0.0006864619
    a2 = 0.0000217523
    a3 = 0.0043348547
    a4 = 0.0008353074
    a5 = -33.4051880
    a6 = 2.77220284
    a7 = 0.003013541
    calcP = b+a1*v1+a2*v2+a3*v3+a4*v4+a5*v5+a6*v6+a7*v7
    return calcP
def promCalidad(cal,c):
    prom=0.0;
    for i in range (c-(Samples+flagS+1),c-(Samples+1),1):
        prom = cal[i]+prom
    prom = prom/flagS
    return prom

try:
  while True:
     GPIO.output(led,0) #Encendemos el LED
     lineBytes = arduino.readline()
     line = lineBytes.decode('utf-8').strip()
     print(line)
     # Separamos los datos recibidos mediante el seprador "|"
     sensorTDS,sensorCO2,porcentajeA,sensorPH,Temp1,Temp2,perfil = line.split(",",7)
     TD.append(int(sensorTDS))
     C.append(int(sensorCO2)) 
     A.append(int(porcentajeA))
     P.append(int(sensorPH))
     t1.append (float(Temp1))
     t2.append (float(Temp2))
     t.append(strftime("%H:%M:%S")) # %Y-%m-%d 
     Q.append(int(perfil))
     tiempo=np.array(t)
     sensor1=np.array(TD)
     sensor2=np.array(C)
     sensor3=np.array(A)
     sensor4=np.array(P)
     sensor5=np.array(t1)
     sensor6=np.array(t2)
     sensor7=np.array(Q)
     
     
     
     cont = cont+1     
     if int(perfil) == 1:
         print("perfil1")
         #pendiente mediana PH
         #deriva de CO2
         deltaCO2 = derivada(derivCO2,C,cont)
         #promedio derivada CO2
         DCO2prom = promedio(DCO2prom,deltaCO2,cont)         
         #deriva de Alcohol
         deltaAL = derivada(derivAL,A,cont)
         #promedio derivada Alcohol
         DALprom = promedio(DALprom,deltaAL,cont)         
         #deriva de Temp1
         deltaT1 = derivada(derivT1,t1,cont)
         dsensorT1=np.array(derivT1)
         #promedio derivada temp1
         DT1prom = promedio(DT1prom,deltaT1,cont)         
         #deriva de Temp2
         deltaT2 = derivada(derivT2,t2,cont)
         #promedio derivada temp2
         DT2prom = promedio(DT2prom,deltaT2,cont)         
         #pendiente desv estandar TDS
         
     elif int(perfil) == 2:
         print("perfil2")
         #promedio acomulado PH
         PHprom = promedio(PHprom,int(sensorPH),cont)
         #maximo CO2
         maxCO2 = maximo(maxCO2,int(sensorCO2))
         #promedio acomulado Alcohol
         ALprom = promedio(ALprom,int(porcentajeA),cont)
         #deriva de Temp1
         deltaT1 = derivada(derivT1,t1,cont)         
         dsensorT1=np.array(derivT1)
         #promedio derivada temp1
         DT1prom = promedio(DT1prom,deltaT1,cont)
         
     elif int(perfil) == 3:
         print("perfil3")
         #promedio acomulado PH
         PHprom = promedio(PHprom,int(sensorPH),cont)
         #promedio acomulado TDS
         TDSprom = promedio(TDSprom,int(sensorTDS),cont)
         #promedio acomulado Alcohol
         ALprom = promedio(ALprom,int(porcentajeA),cont)         
         #deriva de Temp1
         deltaT1 = derivada(derivT1,t1,cont)
         dsensorT1=np.array(derivT1)
         #promedio derivada temp1
         DT1prom = promedio(DT1prom,deltaT1,cont)         
         #deriva de CO2
         deltaCO2 = derivada(derivCO2,C,cont)
         #promedio derivada CO2
         DCO2prom = promedio(DCO2prom,deltaCO2,cont)         
         #minimo T2
         minT2 = minimo(minT2,float(Temp2))     

     data={'tiempo': tiempo,'TDS': sensor1, 'Co2': sensor2, 'Alcohol': sensor3, 'Ph': sensor4, 'Temp1': sensor5, 'Temp2': sensor6, 'Perfil': sensor7 }

     df = pd.DataFrame(data, columns = ['tiempo', 'TDS', 'Co2', 'Alcohol', 'Ph', 'Temp1', 'Temp2', 'Perfil'])
     df2= pd.DataFrame(data, columns = ['tiempo', 'TDS', 'Co2', 'Alcohol', 'Ph', 'Temp1', 'Temp2', 'Perfil'])
     
     df.to_csv('/home/pi/Desktop/cafe/ '+str(nombreA)+'MatrizSensores.csv')
     df2.to_excel('/home/pi/Desktop/cafe/ '+str(nombreA)+'.xlsx',sheet_name='sensores')
   
     #datos=pd.read_csv('/home/pi/Desktop/cafe/ '+str(nombreA)+'MatrizSensores.csv')
     #print(datos)
          
     #archivo=open("/home/pi/Desktop/Fermentador"+str(nombreA)+"MatrizSensores.csv","r")
     
     sleep(0.1) #Esperamos un tiempo para que se vea el parpadeo del LED
     GPIO.output(led,1) #Apagado el LED
     sleep(0.2)
     GPIO.output(led,0) #Apagado el LED
     #sleep(20)
     if int(perfil) > 0 and cont < 3:
         for i in range(int(perfil)):
             GPIO.output(led2,1) #encendido el LED
             sleep(0.2)
             GPIO.output(led2,0) #Apagado el LED
             sleep(0.1) #Esperamos un tiempo para que se vea el parpadeo del LED

     if cont > Samples:
         print("calidad")
         contC.append(cont)
         muestras = np.array(contC)
         #aroma
         if int(perfil)==1:
             #desviacion estandar TDS
             desvTDS = np.std(sensor1)#np.pstdev(sensor1)
             print(desvTDS)
             #median PH
             medianaPH = np.median(sensor4)
             vmedianaPH.append(medianaPH)
             vdesvTDS.append(desvTDS)
             
             print(medianaPH)
             dataCal = calcPerfil1(cont,medianaPH,DCO2prom,DALprom,DT1prom,DT2prom,desvTDS)
             fcalidad.append(dataCal)
             
         #sabor
         elif int(perfil)==2:
             dataCal = calcPerfil2(cont,PHprom,maxCO2,ALprom,DT1prom)
             fcalidad.append(dataCal)
         #acidez
         elif int(perfil)==3:
             dataCal = calcPerfil3(PHprom,cont,TDSprom,ALprom,DT1prom,DCO2prom,minT2)
             fcalidad.append(dataCal)
         
         vDCO2prom.append(DCO2prom)
         vDALprom.append(DALprom)
         vDT1prom.append(DT1prom)
         vDT2prom.append(DT2prom)
         
         vPHprom.append(PHprom)
         vmaxCO2.append(maxCO2)
         vALprom.append(ALprom)
         
         vTDSprom.append(TDSprom)
         vminT2.append(minT2)
         
         SmedianaPH = np.array(vmedianaPH)
         SDCO2prom =np.array(vDCO2prom)
         SDALprom =np.array(vDALprom)
         SDT1prom =np.array(vDT1prom)
         SDT2prom =np.array(vDT2prom)
         SdesvTDS =np.array(vdesvTDS)
         
         SPHprom =np.array(vPHprom)
         SmaxCO2 =np.array(vmaxCO2)
         SALprom =np.array(vALprom)
         
         STDSprom =np.array(vTDSprom)
         SminT2 = np.array(vminT2)
         
         calidad = np.array(fcalidad)
         
         #funcion promedio de diez datos de calidad
         if cont > (Samples+flagS):
             dataCalprom = promCalidad(fcalidad,cont)
             print(dataCalprom)
             
             if dataCalprom > umbralCal: #Verifico que alcance el umbral
                 flagcalprom = 0
                 GPIO.output(led2,1) #encendido el LED
                 
         calp.append(dataCalprom)
         calidadprom = np.array(calp)
         
         #verificar que la calidad no disminuya en un rango de datos
         if cont > (Samples+flagS):
             difcalprom = (calp[cont-(Samples+1)]-calp[cont-(Samples+10)])
             print(difcalprom)
             if difcalprom<-0.2 or flagcalprom ==1:
                 flagcalprom = 1
                 for i in range(10):
                     GPIO.output(led2,1) #encendido el LED
                     sleep(0.1)
                     GPIO.output(led2,0) #Apagado el LED
                     sleep(0.1) #Esperamos un tiempo para que se vea el parpadeo del LED
         
         if cont > (Samples*4):
             for i in range(20):
                 GPIO.output(led2,1) #encendido el LED
                 sleep(0.2)
                 GPIO.output(led2,0) #Apagado el LED
                 sleep(0.2) #Esperamos un tiempo para que se vea el parpadeo del LED

         
         if int(perfil)==1: 
             dataD={'muestras': muestras,'medianaPH': SmedianaPH,'DCO2prom': SDCO2prom,'DALprom': SDALprom,'DT1prom': SDT1prom,'DT2prom': SDT2prom,'desvTDS': SdesvTDS,'calidad': calidad,'calidadprom': calidadprom}
             dfDataD = pd.DataFrame(dataD, columns = ['muestras','medianaPH','DCO2prom','DALprom','DT1prom','DT2prom','desvTDS','calidad','calidadprom'])
         
         elif int(perfil)==2:  
             dataD={'muestras': muestras,'PHprom': SPHprom,'maxCO2': SmaxCO2,'ALprom': SALprom,'DT1prom': SDT1prom,'calidad': calidad,'calidadprom': calidadprom}
             dfDataD = pd.DataFrame(dataD, columns = ['muestras', 'PHprom','maxCO2','ALprom','DT1prom','calidad','calidadprom'])
         
         elif int(perfil)==3:
             dataD={'muestras': muestras,'PHprom': SPHprom,'TDSprom': STDSprom,'ALprom': SALprom,'DT1prom': SDT1prom,'DCO2prom': SDCO2prom,'minT2': SminT2,'calidad': calidad,'calidadprom': calidadprom}
             dfDataD = pd.DataFrame(dataD, columns = ['muestras','PHprom','TDSprom','ALprom','DT1prom','DCO2prom','minT2','calidad','calidadprom'])
         
         #guardar datos de derivadas         
         dfDataD.to_csv('/home/pi/Desktop/cafe/ '+'Perfil'+perfil+str(nombreA)+'.csv')
         dfDataD.to_excel('/home/pi/Desktop/cafe/ '+'Perfil'+perfil+str(nombreA)+'.xlsx',sheet_name='Derivadas')
         

     sleep(5)
     
     
     #print(archivo)
       

     
except KeyboardInterrupt:
	os.system('clear')
	GPIO.cleanup()
	arduino.close()
	print
	print("Programa Terminado por el usuario")
	print
	exit()
