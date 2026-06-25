from pybricks import ev3brick as brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
import struct

# 1. CONFIGURAÇÃO DOS MOTORES
left_motor = Motor(Port.B)   
right_motor = Motor(Port.C)  
lift_motor = Motor(Port.A)   

# Redefine o ângulo atual do motor da empilhadeira como ZERO (na base)
lift_motor.reset_angle(0)

# 2. CONFIGURAÇÃO DA MECÂNICA
TAMANHO_ENGRENAGEM = 24  # Altere aqui para o número de dentes da sua engrenagem circular
TOTAL_DENTES_CREMALHEIRA = 22  # Contados a partir da imagem enviada

# Força ajustada dinamicamente
LIFT_POWER = int(1200 / TAMANHO_ENGRENAGEM)

# Inicialização das variáveis do controle
forward = 0
steering = 0
lift_speed = 0

# Configuração do arquivo do controle
infile_path = "/dev/input/event3"
in_file = open(infile_path, "rb")

FORMAT = 'llHHI'    
EVENT_SIZE = struct.calcsize(FORMAT)
event = in_file.read(EVENT_SIZE)

print("Calibrado na base! Pode pilotar.")

while event:
    (tv_sec, tv_usec, ev_type, code, value) = struct.unpack(FORMAT, event)
    
    # -----------------------------------------------------------------
    # CÁLCULO DE SEGURANÇA (DENTES PERCORRIDOS)
    # -----------------------------------------------------------------
    # Lê o ângulo atual em graus e converte para quantidade de dentes
    angulo_atual = lift_motor.angle()
    dentes_percorridos = (angulo_atual * TAMANHO_ENGRENAGEM) / 360.0

    # -----------------------------------------------------------------
    # LEITURA DOS COMANDOS DO CONTROLE
    # -----------------------------------------------------------------
    if ev_type == 1:
        if code == 304:    # R3 para Cima
            forward = 100 if value == 1 else 0
        elif code == 306:  # R3 para Baixo
            forward = -100 if value == 1 else 0

    elif ev_type == 3:
        # L3: Direção
        if code == 16:
            if value == -1:    steering = -50  
            elif value == 1:   steering = 50   
            elif value == 0:   steering = 0

        # D-PAD: Movimento da Empilhadeira
        elif code == 1:
            if value == 0:      # Quer subir
                lift_speed = LIFT_POWER
            elif value == 255:  # Quer descer
                lift_speed = -LIFT_POWER
            elif value == 128:  # Soltou o botão
                lift_speed = 0

    # -----------------------------------------------------------------
    # TRAVA DE SEGURANÇA (FIM DE CURSO POR SOFTWARE)
    # -----------------------------------------------------------------
    # Se chegou no topo (22 dentes) e o piloto ainda está mandando SUBIR
    if dentes_percorridos >= TOTAL_DENTES_CREMALHEIRA and lift_speed > 0:
        lift_speed = 0
        lift_motor.stop()
        
    # Se chegou na base (0 dentes) e o piloto ainda está mandando DESCER
    elif dentes_percorridos <= 0 and lift_speed < 0:
        lift_speed = 0
        lift_motor.stop()

    # -----------------------------------------------------------------
    # ENVIO DOS COMANDOS PARA OS MOTORES
    # -----------------------------------------------------------------
    left_motor.dc(forward + steering)
    right_motor.dc(forward - steering)
    
    # Só aplica a velocidade se não tiver atingido os limites bloqueantes
    if lift_speed != 0:
        lift_motor.dc(lift_speed)
    else:
        # Mantém o motor travado eletronicamente para a garra não descer com o peso
        lift_motor.stop()

    # Lê o próximo evento do buffer
    event = in_file.read(EVENT_SIZE)

in_file.close()