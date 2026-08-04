#!/usr/bin/env pybricks-micropython
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
import struct
import time 
from uselect import poll, POLLIN

# Inicialização dos Motores Principais
left_motor = Motor(Port.D)   
right_motor = Motor(Port.A)  

motor_b = None
motor_c = None
modo_atual = "Wait"

# Configurações do Elevador
TAMANHO_ENGRENAGEM = 28
TOTAL_DENTES_CREMALHEIRA = 37 
LIFT_POWER = int(1200 / TAMANHO_ENGRENAGEM)

# Variáveis de Controle
forward = 0
steering = 0
aux_speed = 0 

ultimo_check_porta = 0
INTERVALO_CHECK = 2.0  # Poupa processamento do EV3

def verificar_portas():
    global modo_atual, motor_b, motor_c
    
    tem_b = False
    try:
        teste_b = Motor(Port.B)
        tem_b = True
    except Exception:
        tem_b = False

    tem_c = False
    try:
        teste_c = Motor(Port.C)
        tem_c = True
    except Exception:
        tem_c = False

    if tem_b and tem_c:
        if modo_atual != "GARRA":
            motor_b = teste_b
            motor_c = teste_c
            modo_atual = "GARRA"
            
    elif tem_c and not tem_b:
        if modo_atual != "ELEVADOR":
            motor_b = None
            motor_c = teste_c
            motor_c.reset_angle(0)
            modo_atual = "ELEVADOR"
    else:
        if modo_atual != "Wait":
            motor_b = None
            motor_c = None
            modo_atual = "Wait"

infile_path = "/dev/input/event2"
in_file = open(infile_path, "rb")

poller = poll()
poller.register(in_file, POLLIN)

FORMAT = 'llHHi'    
EVENT_SIZE = struct.calcsize(FORMAT)

verificar_portas()

print("Robô Inicializado. Pronto para rodar!")

while True:
    if poller.poll(10):  # Aguarda até 10ms por um comando do controle
        event = in_file.read(EVENT_SIZE)
        if not event:
            break

        (tv_sec, tv_usec, ev_type, code, value) = struct.unpack(FORMAT, event)

        if ev_type == 3: # Sensores analógicos / D-Pad
            if code == 17:    # D-pad vertical
                if value == -1: # Para cima
                    forward = 100
                elif value == 1: # Para baixo
                    forward = -100
                else: # Solto
                    forward = 0
            elif code == 16: # D-pad horizontal
                if value == -1: # Para a esquerda
                    steering = -50
                elif value == 1: # Para a direita
                    steering = 50
                else: # Solto
                    steering = 0
                
        elif ev_type == 1:  # Botões (Pressionar / Soltar)
            if code == 308:   # Botão Y 
                if value == 1:  # Pressionado
                    aux_speed = 100
                    if modo_atual == "GARRA" and motor_b and motor_c:
                        try:
                            motor_b.run_angle(500, 90, wait=False) 
                            motor_c.run_angle(500, 90, wait=False)
                        except Exception:
                            pass
                elif value == 0: # Soltado
                    aux_speed = 0

            elif code == 304: # Botão A
                if value == 1: # Pressionado
                    aux_speed = -100
                    if modo_atual == "GARRA" and motor_b and motor_c:
                        try:
                            motor_b.run_angle(-500, 90, wait=False)
                            motor_c.run_angle(-500, 90, wait=False)
                        except Exception as e: print("Erro na garra:", e)
                elif value == 0: # Soltado
                    aux_speed = 0

    #ESTES BLOCOS AGORA RODAM CONTINUAMENTE
    
    # Verificação periódica de portas conectadas
    tempo_agora = time.time()
    if tempo_agora - ultimo_check_porta > INTERVALO_CHECK:
        verificar_portas()
        ultimo_check_porta = tempo_agora

    # Movimentação em tempo real do Chassi (para imediatamente ao soltar o D-pad)
    left_motor.dc(forward + steering)
    right_motor.dc(forward - steering)

    # Controle Contínuo e Proteção do Elevador (ativado quando descomentar)
    try:
        if modo_atual == "ELEVADOR" and motor_c:
            forca_elevador = LIFT_POWER if aux_speed > 0 else -LIFT_POWER
            if aux_speed == 0: 
                forca_elevador = 0

            angulo_atual = motor_c.angle()
            dentes_percorridos = (angulo_atual * TAMANHO_ENGRENAGEM) / 360.0

            if dentes_percorridos >= TOTAL_DENTES_CREMALHEIRA and forca_elevador > 0:
                motor_c.stop()
            elif dentes_percorridos <= 0 and forca_elevador < 0:
                motor_c.stop()
            elif forca_elevador != 0:
                motor_c.dc(forca_elevador)
            else:
                motor_c.stop()
    except Exception:
        pass

    time.sleep(0.01)#pausa estrategica

in_file.close()