#!/usr/bin/env pybricks-micropython
from pybricks.ev3devices import Motor
from pybricks.parameters import Port

import struct
import time 
from uselect import poll, POLLIN

#Inicialização dos Motores Principais
left_motor = Motor(Port.D)   
right_motor = Motor(Port.A) 

elevator_motor = Motor(Port.C)   
claw_motor = Motor(Port.B)

claw_motor.reset_angle(0)
elevator_motor.reset_angle(0)


# Configurações do Elevador
GEAR_SIZE = 29
RACK_SIZE = 38
LIFT_POWER = int(1200 / GEAR_SIZE)

# Variáveis de Controle
forward = 0
steering = 0
aux_speed = 0 

infile_path = "/dev/input/event2"
in_file = open(infile_path, "rb")

poller = poll()
poller.register(in_file, POLLIN)

FORMAT = 'llHHi'    
EVENT_SIZE = struct.calcsize(FORMAT)

print("Robô Inicializado. Pronto para rodar!")

while True:#repete sempre
    if poller.poll(10):  # Aguarda até 10ms por um comando do controle
        event = in_file.read(EVENT_SIZE)
        if not event:
            break

        (tv_sec, tv_usec, ev_type, code, value) = struct.unpack(FORMAT, event)

        if ev_type == 3: # Sensores analógicos / D-Pad
            if code == 17:    # D-pad vertical
                if value == -1: # Para cima
                    print("Para frente")
                    forward = 100
                elif value == 1: # Para baixo
                    print("Para trás")
                    forward = -100
                else: # Solto
                    forward = 0
            elif code == 16: # D-pad horizontal
                if value == -1: # Para a esquerda
                    print("Para a esquerda")
                    steering = -50
                elif value == 1: # Para a direita
                    print("Para a direita")
                    steering = 50
                else: # Solto
                    steering = 0
                
        elif ev_type == 1:  # Botões (Pressionar / Soltar)
            if code == 311:   # Botão RT - Claw
                if value == 1:  # Pressionado
                    print("Subir claw")
                    claw_motor.dc(500)
                elif value == 0: # Soltado
                    claw_motor.stop()

            elif code == 310: # Botão LT
                if value == 1: # Pressionado
                    print("Descer claw")
                    claw_motor.dc(-500)
                elif value == 0: # Soltado
                    claw_motor.stop()

            elif code == 304:   # Botão Y - Elevator
                if value == 1:  # Pressionado
                    print("Subir elevador")
                    aux_speed = 500
                elif value == 0: # Soltado
                    aux_speed = 0
            elif code == 306: # Botão A
                if value == 1: # Pressionado
                    print("Descer elevador")
                    aux_speed = -500
                elif value == 0: # Soltado
                    aux_speed = 0

    left_motor.dc(forward + steering)# movimentacao basica
    right_motor.dc(forward - steering)
    
    forca_elevador = LIFT_POWER if aux_speed > 0 else -LIFT_POWER
    aux_speed == 0
    if forca_elevador != 0:

        angulo_atual = elevator_motor.angle()
        dentes_percorridos = (angulo_atual * GEAR_SIZE) / 360.0

        if dentes_percorridos >= RACK_SIZE and forca_elevador > 0:
            elevator_motor.stop()
        elif dentes_percorridos <= 0 and forca_elevador < 0:
            elevator_motor.stop()
        elif forca_elevador != 0:
            elevator_motor.dc(forca_elevador)
        else:
            elevator_motor.stop()

    # Pequena pausa para não sobrecarregar o processador do EV3
    time.sleep(0.01)

in_file.close()