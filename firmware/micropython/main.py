
# cliente seguidor de precio para cripto monedas en el exchange binance este programa permite la visulizacion de precio en tiempo real de dos cripto monedas ...
# ... por medio de una pantalla lcd 16*2 con ayuda de arduino y el puerto serie, el arduino puede ser replazado anadiendo un Módulo adaptador LCD a I2C a la placa esp32
# el valor de las alarma solo funciona para la primer moneda la segunda moneda se usa como una referencia adicional

#importando librerias necesarias
import urequests
import utime
import _thread
from machine import UART

# este programa ejecuta dos funciones al tiempo en 2 hilos la funcion web() maneja la pagina web quien recibe los datos que el cliente desea ver.
# mientras la funcion ticker() realiza la solicitud de los valores de las monedas y analiza los precios del mercado comparando los valores fijados en las alarmas ...
# ... y envia los datos a arduino para actualizar el valor en la pantalla lcd ademas gestina la activacion de la alarma sonora medinte un buzzer el cual se configuo en el boot.py en el puerto 32



#funcion para lanzar el cliente
def web():

  global alarms_up # valores para fijar alarma en subida
  global alarms_down # valores para fijar alarma en bajada
  global predo_coins # monedas a rastrear por defecto al iniciar el sistema

  
  #control del sitio web
  def web_page(alarms_up, alarms_down):
    #au y ad muestran los valores a los que el usuaruio fija las alarmas
    au = ' '.join(map(str, sorted(alarms_up)))
    ad = ' '.join(map(str, sorted(alarms_down)))

    #codigo html y css
    html =    """<html>
                    <head> 
                      <title>ESP32 Crypto Ticker</title> 
                      <meta name="viewport" content="width=device-width, initial-scale=1">
                      <meta http-equiv="refresh" content="30; url=/">
                      <link rel="icon" href="data:,"> 
                      <style>
                        html{
                            font-family: Helvetica; 
                            display:inline-block;
                            margin: 0px auto; 
                            text-align: center;
                          }
                          
                          h1  {
                              color: #0F3376; 
                              padding: 2vh;
                            }
                          
                          p   { 
                            font-size: 1rem;
                            }
                          .button{
                              display: inline-block; 
                              background-color: #e7bd3b;
                              border: none;
                              border-radius: 4px;
                              color: white;
                              padding: 16px 40px;
                              text-decoration: none;
                              font-size: 30px;
                              margin: 2px; 
                              cursor: pointer;
                              }

                          .button2{
                              background-color: #ff0000;
                              }

                          .button3{
                              background-color: #008f39;
                              }

                        </style>
                      </head>

                      <body> 

                        <h1>ESP32 Crypto Ticker</h1>
                          <p>Alerta Mayor que: <strong>"""+au+"""<br><br></strong></p> 
                          <p>Alerta Menor que: <strong>"""+ad+"""<br><br></strong></p>
                          <input type="text" placeholder="Alerta..." id="myInput">
                          <p>Finalice con letra "u" para alertas de subida, o con "d" para alertas de baja.</p><br>
                          <button type="button"  class="button" onclick="addAlarm();">Agregar Alarma</button>
                          <button type="button"  class="button button2" onclick="delAlarm();">Borrar Alarma</button>
                          <br><br><input type="text" placeholder="Moneda..." id="myInput2">
                          <p>Ingrese las siglas de la moneda y finalice con 1 para visulizar en la primera posicion del LCD y con 2 para la segunda.</p><br>
                          <button type="button"  class="button button3" onclick="addCoin();">Cambiar Moneda</button>





                        <script>

                            function addAlarm(){
                              var inputVal = document.getElementById("myInput").value;
                              if (inputVal.length > 0) {
                                window.location.replace("/?$="+inputVal+"@");
                              }
                              
                            }

                            function delAlarm(){
                              var inputVal = document.getElementById("myInput").value;
                              if (inputVal.length > 0) {
                                window.location.replace("/?&="+inputVal+"@");
                              }
                              
                            }


                            function addCoin(){
                              var inputVal = document.getElementById("myInput2").value;
                              if (inputVal.length > 0) {
                                window.location.replace("/?!="+inputVal+"@");
                              }
                              
                            }


                      </script>

                      </body>

                  </html>"""
    
    return html

  #lista para guardar los valores de las alarmas de precio de subida y bajada
  alarms_up = []
  alarms_down = []
  #monedas a segiur predeterminadas litecoin y bitcoin
  predo_coins = ["LTC","BTC"]

  #conectando con el servidor para escuchar
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind(('', 80))
  s.listen(5)

  #ciclo de control
  while True:
     #aceptando la conexion con el servidor
    conn, addr = s.accept()
    request = conn.recv(1024)
    request = str(request)

    #caracteres para diferenciar acciones de control dentro de la peticion
    set_alarm = request.find('$')
    del_alarm = request.find('&')
    add_coin =  request.find('!')
  
    
    # se verifica que peticion se hizo al recibir el request en pasicion 8 del string se compara
    if set_alarm == 8:
      #se extrae el dato del numero para fijar la alarma el caracter '@' indica donde finaliza el comando
      alarm = request[request.find('$')+2:request.find('@')-1]
      # se convierte a numero flotante
      alarm = round(float(alarm),2)
      #se define si el valor de la alarma de precio debe ser de subida o baja y se almacena en la lista correspondiente, si el numero finaliza en 'u' es de subida si fibaliza en 'd' es de bajada
      if request[request.find('@')-1] == "u":
        #verifica si el valor ya exite sino se anade a la lista
        if alarms_up.count(alarm) == 0:
          alarms_up.append(alarm)
      
      elif request[request.find('@')-1] == "d":
        
        if alarms_down.count(alarm) == 0:
          alarms_down.append(alarm)
    #verifica si la accion requerida es para eliminar una valor de la alrma si esta se encuntra dentro de las listas entonces se borra
    if del_alarm == 8:
      alarm = request[request.find('&')+2:request.find('@')-1]
      alarm = round(float(alarm),2)
      if request[request.find('@')-1] == "u":
        if alarms_up.count(alarm) == 1:
          alarms_up.remove(alarms_up[alarms_up.index(alarm)])
      elif request[request.find('@')-1] == "d":
        if alarms_down.count(alarm) == 1:
          alarms_down.remove(alarms_down[alarms_down.index(alarm)])
    #verifica si se hace la solicitud para cambiar la moneda a rastrear y la posicion en la que desa que esta se vean en la pantalla la posicion 1 se fija la moneda a rasterar la psocion dos se usa como referencia
    if add_coin == 8:
      coin = request[request.find('!')+2:request.find('@')-1]
      if request[request.find('@')-1] == "1":
        predo_coins[0] = coin.upper()
        alarms_up = []
        alarms_down = []
      elif request[request.find('@')-1] == "2":
        predo_coins[1] = coin.upper()



      
    #se actuliza la pagina luego de tomar accion se actualizan los datos de las alrmas fijadas
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    #lanza la pagina al recibir una peticion
    conn.sendall(web_page(alarms_up,alarms_down))
    conn.close()



#control de la alrma y obtencion del precio de las monedas mediante la api de binance
def ticker():
  #configuracion de la coneccion serial 
  uart = UART(1, 9600, tx=19, rx=18)
  uart.init(9600, bits=8, parity=None, stop=1) 

  #funcion para controlar el buzzer realiza tres pitidos al activarce la alarma
  def act_buzz():
    for i in range(3):
      buzz.value(1)
      utime.sleep_ms(400)
      buzz.value(0)
      utime.sleep_ms(500)
      buzz.value(1)
      utime.sleep_ms(400)
      buzz.value(0)
      utime.sleep_ms(1000)

  #funcion que activa la alarma
  def alarm_on(price):
    activate_alarm = False
    #verifica si el valor del precio es igual o mayor a los precios fijados para las arlarmas de subida 
    for i in alarms_up:
      if price >= i:
        #se elimina el valor de la lista de las alarmas de subida
        alarms_up.remove(alarms_up[alarms_up.index(i)])
        #se activa la funcion del buzzer
        activate_alarm = True
        
    #verifica si el valor del precio es igual o mayor a los precios fijados para las arlarmas de bajda
    for j in alarms_down:
      if price <= j:
        alarms_down.remove(alarms_down[alarms_down.index(j)])
        activate_alarm = True
    #se llama la funcion de control del buzzer
    if activate_alarm:
      act_buzz()
      activate_alarm = False
      
  #ciclo de control 
  while True:
    #se conecta con el api de binance si no da respuesta se espera y se maneja los errores de valores u otro tipo
    try:
      #se trea los valores de las monedas congifuradas anteririmente por defecto solicita litecoin y bitcoin
      coin1 = urequests.get('https://api.binance.com/api/v3/ticker/price?symbol='+predo_coins[0]+'USDT').json()
      utime.sleep_ms(50)
      coin2 = urequests.get('https://api.binance.com/api/v3/ticker/price?symbol='+predo_coins[1]+'USDT').json()
      #se extrae el simbolo y los valores del precio actual
      coin1_price = coin1.get('symbol') + '=' + coin1.get('price') 
      coin2_price = coin2.get('symbol') + '=' + coin2.get('price')
      #se envian los datos para ser mostrados en la pantalla lcd a traves de arduino
      prices =  coin1_price+"$"+coin2_price+":"
      uart.write(prices)
      #activa la funcion para evaluar el precio actual con los valores establecidos en las alarmas y activar el buzzer
      alarm_on(round(float(coin1.get('price')),2))
    #manejo de errores en los datos
    except ValueError:
      uart.write("Connection Error$Please Wait...  :")
      utime.sleep_ms(5000)


    #manejo de errores en el sistema
    except OSError as err:
      uart.write("Connection Error$Please Wait...  :")
      utime.sleep_ms(5000)
      
      


#se inician los hilos para ejecutar las tareas
_thread.start_new_thread(web,())
_thread.start_new_thread(ticker,())


