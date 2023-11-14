from machine import Pin
import time
import network,urequests
from bme280_float import *
from dht import DHT11
from time import sleep
from machine import Pin, I2C

try:
  import usocket as socket
except:
  import socket

import esp
esp.osdebug(None)

import gc
gc.collect()

ssid='FAMILIA SUAREZ'
password='william8080'
url="https://api.thingspeak.com/update?api_key=JVQIE6AG8HDO7J61&field1=0"

red=network.WLAN(network.STA_IF)
red.active(True)
red.connect(ssid,password)

while red.isconnected()==False:
    pass

print('conexion correcta')
print(red.ifconfig())

i2c = I2C(1,scl=Pin(22), sda=Pin(21), freq=400000)
sensorDHT = DHT11(Pin(23))

led = Pin(2, Pin.OUT)
rele =  Pin(19,Pin.OUT)
pin18=Pin(18,Pin.IN,Pin.PULL_DOWN);

cont=0;
def contador(pin):
    global cont;
    cont+=1;
    
pin18.irq(trigger=Pin.IRQ_RISING,handler=contador);

def web_page(t1,p1,h1,a1,w1):
  if rele.value() == 1:
    gpio_state="Encendido"
    temperatura=str(t1)
    presion=str(p1)
    humedad=str(h1)
    altitud1=str(a1)
    rpm=str(w1)
  else:
    gpio_state="Apagado"
    temperatura="--"
    presion="--"
    humedad="--"
    altitud1="--"
    rpm="--"
  
  html = """<html>
  <head>
     <title>Proyecto estación meteorologica</title> <meta name="viewport" content="width=device-width, initial-scale=1">
     <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
     h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
     border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
     .button2{background-color: #4286f4;}</style>
  </head>
  <body>
      <h1>Proyecto estacion Meteorologica ESP32</h1>
      <hr></hr>
      <h3>Integrantes</h3>
      <h3> -> William Suarez Ortiz</h3>
      <h3> -> </h3>
      <h3> -> </h3>
      <hr></hr>
      <h3>Módulo de control</h3>
      <p>Estado: <strong>""" + gpio_state + """</strong></p><p><a href="/?led=on"><button class="button">ON</button></a></p>
      <p><a href="/?led=off"><button class="button button2">OFF</button></a></p>
      <hr></hr>
      <h3>Condiciones Ambientales</h3>
      <p>Temperatura : <strong>"""+temperatura+"""</strong> °C</p>
      <p>Presion : <strong>"""+presion+"""</strong> Pa</p>
      <p>Humedad : <strong>"""+humedad+"""</strong> %</p>
      <p>Altitud : <strong>"""+altitud1+"""</strong> m.s.n.m</p>
      <p>Velocidad : <strong>"""+rpm+"""</strong> rpm</p>
  </body></html>"""
  return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    sleep(1)
    rev1=cont/20;
    rev1_s=rev1/1;
    rev1_min=rev1_s*60;
    sensorDHT.measure()
    bme = BME280(i2c=i2c)
    valores=bme.read_compensated_data()
    hum = sensorDHT.humidity()    
    pres = valores[1]
    temp = valores[0]
    hum1 = valores[2]
    altitud = bme.altitude
    respuesta=urequests.get(url+"&field1="+str(temp)+"&field2="+str(hum)+"&field3="+str(pres)+"&field4="+str(altitud)+"&field5="+str(rev1_min))
    respuesta.close()
    print('Temepartura : '+str(temp)+' °C - Humedad : '+str(hum)+'% - Presion : '+str(pres)+'Pa - Altitud : '+str(altitud)+'m.s.n.m - Velocidad : '+str(rev1_min)+' rpm')
    
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    request = str(request)
    print('Content = %s' % request)
    led_on = request.find('/?led=on')
    led_off = request.find('/?led=off')
    if led_on == 6:
        print('LED ON')
        rele.value(1)
    if led_off == 6:
        print('LED OFF')
        rele.value(0)  
    response = web_page(temp,hum,pres,altitud,rev1_min)
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()
    
    cont=0