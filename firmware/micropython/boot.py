
# Servidor Crypto ticker

#importando librerias necesarias
try:
	import usocket as socket
except:
	import socket

from machine import Pin
import network

import esp
esp.osdebug(None)

import gc
gc.collect()

import utime
from machine import UART

#configuracion para conexion serial con arduino para traferir datos
uart = UART(1, 9600, tx=19, rx=18)
uart.init(9600, bits=8, parity=None, stop=1)

# credenciales para conectase con la red 
ssid = 'nombre de la red aqui' 
password = 'contrasena aqui'

#configurando  Conexion
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

#esperando hasta obtener conexion y establecer una ip
while station.isconnected() == False:
	uart.write("waiting...      $waiting...      :")

#enviando datos con direccion de ip por puerto serial a arduino para mostrar en lcd 16*2, el carater '$' y ':' funcinan para inidcar fibal de linea
uart.write('Connected ;)    $'+station.ifconfig()[0]+"    :")
utime.sleep(5)

#configurando pin para alarma
buzz = Pin(32, Pin.OUT)