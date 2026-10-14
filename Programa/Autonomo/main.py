#!/usr/bin/env pybricks-micropython 
from pybricks.ev3devices import Motor, UltrasonicSensor 
from pybricks.parameters import Port 
from pybricks.tools import StopWatch, wait 


left_motor = Motor(Port.D) 
right_motor = Motor(Port.A) 
claw_motor = Motor(Port.B) 
distance_sensor = UltrasonicSensor(Port.S1) 

VELOCIDADE = 50 
DISTANCIA_PARA_DETECÇÃO = 150 #EM MILÍMETROS (15 CM)
print("Iniciando...") 

while True:
    timer = StopWatch() #para o timer


    timer.reset() #zera o timer
    left_motor.dc(VELOCIDADE) #começa a andar
    right_motor.dc(VELOCIDADE) 

    while distance_sensor.distance() > DISTANCIA_PARA_DETECÇÃO: wait(10) 
    #achou algo!
    tempo_andado = timer.time() 
    left_motor.stop() 
    right_motor.stop() 
    print("Objeto detectado! Tempo andado:", tempo_andado) 
    wait(500) 

    claw_motor.run_angle(300, 120) 

    wait(500) 

    left_motor.dc(-VELOCIDADE) 
    right_motor.dc(-VELOCIDADE) 
    wait(tempo_andado) 

    left_motor.stop() 
    right_motor.stop() 
    
    wait(5000)