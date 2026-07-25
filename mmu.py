from machine import UART, Pin, PWM
from time import sleep_ms

uart = UART(
    0,
    baudrate=115200,
    tx=Pin(0),
    rx=Pin(1),
    bits=8,
    parity=None,
    stop=1
)

buffer = bytearray()

TESTE_SEM_FILAMENTO = False

# Configuração do Servo Motor
class ServoMotor:
    def __init__(self, pino_numero, freq=50):
        self.pwm = PWM(Pin(pino_numero))
        self.pwm.freq(freq)

        self.min_pulse = 500
        self.max_pulse = 2500

    def mover_para_angulo(self, angulo):
        angulo = max(0, min(180, angulo))

        pulso = self.min_pulse + (
            angulo / 180.0
        ) * (self.max_pulse - self.min_pulse)

        periodo_us = 1_000_000 / self.pwm.freq()
        duty = int((pulso / periodo_us) * 65535)

        self.pwm.duty_u16(duty)

        print(
            "Servo:",
            angulo,
            "graus |",
            int(pulso),
            "us | duty:",
            duty
        )

    def posicao_inicial(self):
        """Posição inicial do servo: 0°."""
        self.mover_para_angulo(0)

    def posicao_repouso(self):
        """Posição de repouso: 0°."""
        self.mover_para_angulo(0)

    def posicao_ativa(self):
        """Posição ativa: 180°."""
        self.mover_para_angulo(180)

# Inicializa o servo no pino GP15 (altere conforme necessário)
servo = ServoMotor(15)
servo.posicao_repouso()
sleep_ms(1000)  # Aguarda o servo se estabilizar

def enviar(texto):
    uart.write(texto + "\n")

def filament_present():
    # Substituir pela leitura real do sensor FINDA
    return False

def processar(comando):
    print("Marlin:", comando)

    if comando == "X0":
        # Reinicializar o estado interno da MMU
        servo.posicao_repouso()  # Servo volta ao repouso
        enviar("start")

    elif comando == "S1":
        enviar("1ok")

    elif comando == "S2":
        enviar("126ok")

    elif comando == "P0":
        if TESTE_SEM_FILAMENTO:
            enviar("0ok")
        else:
            enviar("1ok")

    elif comando.startswith("T"):
        # Mudança de filamento - Ativa o servo
        try:
            numero_filamento = int(comando[1:])
            print(f"Mudando para filamento {numero_filamento}")
            
            # Move o servo para posição ativa
            servo.posicao_ativa()
            sleep_ms(500)  # Aguarda movimento do servo
            
            # Volta o servo para posição inicial
            servo.posicao_inicial()
            sleep_ms(500)
        except ValueError:
            pass
        
        enviar("ok")

    elif comando.startswith("L"):
        try:
            numero_filamento = int(comando[1:])
            print(f"Carregando filamento {numero_filamento}")

            servo.mover_para_angulo(180 / 5 * numero_filamento)  # Ajuste conforme necessário
            sleep_ms(2500)  # Aguarda o servo se estabilizar

            enviar("ok")
        except ValueError:
            pass

    elif comando.startswith("C"):
        # Color/Change
        print("Mudança de cor...")
        enviar("ok")

    elif comando.startswith("U"):
        # Unload filamento
        print("Descarregando filamento...")
        enviar("ok")

    elif comando.startswith("E"):
        # Eject filamento
        print("Ejetando filamento...")
        enviar("ok")

    elif comando.startswith("R"):
        # Reset/Recover
        print("Reset...")
        servo.posicao_repouso()
        enviar("ok")

    elif comando.startswith("F"):
        # Position feedback
        print("Feedback de posição...")
        enviar("ok")

    elif comando == "A":
        # Interromper a operação atual
        servo.posicao_repouso()
        enviar("ok")

# Avisa que a controladora MMU iniciou
enviar("start")

while True:
    dados = uart.read()

    if dados:
        buffer.extend(dados)

        while b"\n" in buffer:
            linha, restante = buffer.split(b"\n", 1)
            buffer = bytearray(restante)

            comando = linha.strip().decode("ascii")
            if comando:
                processar(comando)

    sleep_ms(1)