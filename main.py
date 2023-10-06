#Monitor de carga con panel solar

#23-06-22
#Ver 8
#Mueve la definición del sensor de distancias
#Agrega definiciones de medidas del tanque al inicio
#Limita DistanciaMetros a Profundidad


#06/06/22
#Ver 7: Si la distancia medida es menor a cero, se fija a 0

#01/02/21
#Ver 6: Usa WDT sobre todo por la falta de timeout de urequests

#30/01/21
#Ver 5: Incluye el medidor de distancias

#29/01/21
#Ver 4.1: Manda a TS el nombre de la red WiFi

#18/01/21
#Ver 4: Incluye try y except por si no logra alcanzar al servidor

#Ver 3: Si no logra conectar a la red Wfi se duerme por 5 minutos
#18/01 Al no tener la red se descargo la bat. Subo el tiempo de reconexion a 15 min y no prendo el led

#Mapeo de GPIO de D1 Mini

D0 = 16
D1 = 5
D2 = 4
D3 = 0
D4 = 2
D5 = 14
D6 = 12
D7 = 13
D8 = 15

#Dimensiones del tanque
Profundidad = 1.03  #m - Del fondo a la sup del agua (max)
Superficie  = 0.636 #m2 - superficie del fondo



import network, time, urequests, machine
from hcsr04 import HCSR04 

def conectaWifi (red, password):
      global miRed
      miRed = network.WLAN(network.STA_IF)     
      if not miRed.isconnected():              #Si no está conectado…
          miRed.active(True)                   #activa la interface
          miRed.connect(red, password)         #Intenta conectar con la red
          print('Conectando a la red', red +"…")
          timeout = time.time ()
          while not miRed.isconnected():           #Mientras no se conecte..
              wdt.feed ()
              if (time.ticks_diff (time.time (), timeout) > 10):
                  return False
      return True

#Delay para tomar el control desde Thonny
time.sleep (3)

medidor = HCSR04 (trigger_pin=D2 , echo_pin=D1 )
time.sleep (1)
    
conversor = machine.ADC (0)
rtc = machine.RTC()
wdt = machine.WDT() #Solo para recordar, es constante   
wdt.feed()



print ("RESET:",machine.reset_cause())


#red="Los Tolo3"
red="Tolocka2"
password="tolocka3239"

#while (True):
#    try:
#        distancia = medidor.distance_cm ()
#        print ("Distancia = ", distancia)
#        time.sleep (10)
#    except:
#        print ("Error!")


if conectaWifi (red, password):

    wdt.feed()

    print ("Conexión exitosa!")
    print('Datos de la red (IP/netmask/gw/DNS):', miRed.ifconfig())
    
    url= "https://api.thingspeak.com/update?api_key=Y0MF9YJJ1KSTHMOQ"
    
    bat = conversor.read()
    voltios = (bat*5)/1023
    print (voltios)
    
    nivelRed =miRed.status('rssi')
    print ("RSSI=",nivelRed," dBm")
    
    
    #distancia = medidor.distance_cm ()
    distancia=10
    
    print ("Distancia = ", distancia)
       
    DistanciaMetros = distancia/100
    
    #Limitar por si se pasa (por error)
    if (DistanciaMetros > Profundidad):
        DistanciaMetros = Profundidad
        
    metros = Superficie * (Profundidad - DistanciaMetros)
    litros = metros * 1000
    print ("Litros =",litros)
    
    #time.sleep (2)
    
    wdt.feed ()
    
    try:
        #Enviar datos al servidor
        respuesta = urequests.get(url+"&field1="+str(voltios)+"&field2="+str(distancia)+"&field3="+str(nivelRed)+"&field4="+str(litros))
    
    except:
        print ("Error al reportar")
        tiempoAlarma = 15*60000
    
    else:
        print(respuesta.text)
        print (respuesta.status_code)
        respuesta.close ()
    
        #Dormir por 1 hora
        tiempoAlarma = 60*60000
 
else:
    print ("Imposible conectar")
        
    #Dormir por 15 minutos para reintentar la conexión
    tiempoAlarma = 15*60000


miRed.active (False)

#led.on ()  #Apaga el led (Esta al reves)

  

#Configura la alarma para resetear y despertar al micro
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)  
rtc.alarm(rtc.ALARM0, tiempoAlarma)  

#A dormir



print ("A dormir ",tiempoAlarma)
machine.deepsleep()