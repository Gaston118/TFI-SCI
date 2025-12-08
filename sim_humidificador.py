# ------------------------------------------------------------
# Script: simulacion_humidificador.py
# Propósito:
#   Simular cuánto tiempo tarda un recinto en alcanzar una
#   humedad relativa objetivo, considerando:
#     - Aporte del humidificador
#     - Pérdidas por renovación de aire (ACH)
#     - Pérdidas por condensación
#
# Unidades:
#   Masa: gramos (g)
#   Tiempo: minutos (min)
#   Volumen: metros cúbicos (m^3)
#   Temperatura: grados Celsius (°C)
#   ACH: renovaciones de aire por hora (h^-1)
#
# Modelo físico (balance de masa de vapor):
#
#   d(rho_v)/dt = (dotm / V) - a*(rho_v - rho_out) - k_cond/V
#
# donde:
#   rho_v(t)  = densidad de vapor dentro del recinto [g/m^3]
#   dotm      = caudal másico del humidificador [g/min]
#   V         = volumen del recinto [m^3]
#   a         = ACH/60 [1/min]
#   rho_out   = densidad de vapor del aire exterior [g/m^3]
#   k_cond    = pérdidas por condensación [g/min]
#
# El modelo se integra numéricamente con paso de tiempo pequeño.
# Además se impone el TOPE FÍSICO de saturación:
#   rho_v ≤ rho_sat(T)
# ------------------------------------------------------------

import math
import numpy as np
import matplotlib.pyplot as plt


# ------------------------------------------------------------
# Presión de vapor de saturación (fórmula de Magnus)
# ------------------------------------------------------------
def presion_saturacion(T_c):
    """
    Devuelve la presión de vapor de saturación en hPa
    para una temperatura T en °C.
    """
    return 6.112 * math.exp((17.62 * T_c) / (243.12 + T_c))


# ------------------------------------------------------------
# Densidad de vapor de saturación en g/m^3
# ------------------------------------------------------------
def rho_saturacion(T_c):
    """
    Devuelve la densidad de vapor de agua a 100% HR
    en g/m^3 para una temperatura T en °C.
    """
    e_s = presion_saturacion(T_c)  # hPa
    T_k = T_c + 273.15             # Kelvin
    rho = 216.7 * e_s / T_k
    return rho


# ------------------------------------------------------------
# Densidad de vapor real a partir de HR y temperatura
# ------------------------------------------------------------
def rho_desde_HR(HR, T_c):
    """
    Convierte humedad relativa (%) y temperatura (°C)
    en densidad absoluta de vapor [g/m^3].
    """
    return (HR / 100.0) * rho_saturacion(T_c)


# ------------------------------------------------------------
# Simulación principal
# ------------------------------------------------------------
def simular_relleno(
        V=0.2,           # Volumen del recinto [m^3]
        dotm=3.3,        # Caudal del humidificador [g/min]
        T=20.0,          # Temperatura interior [°C]
        HR0=0.0,         # Humedad inicial interior [%]
        HR_out=40.0,     # Humedad exterior [%]
        ACH=1.0,         # Renovaciones de aire por hora [h^-1]
        k_cond=0.15,     # Pérdida por condensación [g/min]
        modo_cond='fijo',  # 'fijo' o 'proporcional'
        dt=0.01,         # Paso de integración [min]
        HR_objetivo=100.0, # Humedad objetivo [%]
        tiempo_max=60.0   # Tiempo máximo de simulación [min]
    ):
    """
    Simula la evolución de la humedad dentro del recinto.
    Devuelve el tiempo necesario para llegar a la HR objetivo.
    """

    rho_sat = rho_saturacion(T)                 # Densidad de saturación [g/m^3]
    rho_v = rho_desde_HR(HR0, T)                # Estado inicial [g/m^3]
    rho_out = rho_desde_HR(HR_out, T)           # Exterior [g/m^3]
    a = ACH / 60.0                              # Coef. de ventilación [1/min]

    tiempos = [0.0]
    rhos = [rho_v]
    masa_condensada = 0.0
    masa_inyectada = 0.0

    rho_objetivo = (HR_objetivo / 100.0) * rho_sat
    pasos_max = int(tiempo_max / dt)

    for i in range(pasos_max):
        t = (i + 1) * dt

        # Masa inyectada por el humidificador en este paso
        masa_in = dotm * dt

        # Masa actual en el recinto
        masa_actual = rho_v * V

        # Caudal volumétrico de aire por ventilación
        Q = ACH * V / 60.0   # m^3/min

        # Pérdida por ventilación
        perdida_vent = Q * (rho_v - rho_out) * dt

        # Pérdida por condensación
        if modo_cond == 'fijo':
            perdida_cond = min(k_cond * dt, max(0.0, masa_actual))
        else:
            exceso = max(0.0, rho_v - rho_sat)
            perdida_cond = exceso * V * k_cond * dt

        # Balance de masa
        nueva_masa = masa_actual + masa_in - perdida_vent - perdida_cond
        nuevo_rho = max(0.0, nueva_masa / V)

        # Límite físico de saturación
        if nuevo_rho > rho_sat:
            exceso = (nuevo_rho - rho_sat) * V
            masa_condensada += exceso
            nuevo_rho = rho_sat

        masa_inyectada += masa_in
        masa_condensada += perdida_cond

        rho_v = nuevo_rho
        tiempos.append(t)
        rhos.append(rho_v)

        # Condición de llegada al objetivo
        if rho_v >= rho_objetivo:
            return tiempos, rhos, t, masa_inyectada, masa_condensada, rho_sat

    return tiempos, rhos, None, masa_inyectada, masa_condensada, rho_sat


# ------------------------------------------------------------
# EJECUCIÓN DEL EJEMPLO
# ------------------------------------------------------------
if __name__ == "__main__":

    V = 0.2
    dotm = 3.3
    T = 20.0
    HR0 = 0.0
    HR_out = 20.0
    ACH = 10.0
    k_cond = 0.55
    modo_cond = 'fijo'  # 'fijo' o 'proporcional'
    dt = 0.05
    HR_objetivo = 100.0

    tiempos, rhos, t_obj, masa_in, masa_cond, rho_sat = simular_relleno(
        V, dotm, T, HR0, HR_out, ACH,
        k_cond, modo_cond, dt, HR_objetivo
    )

    if t_obj is not None:
        print(f"Se alcanzó el {HR_objetivo:.1f}% de HR en {t_obj*60:.1f} segundos")
    else:
        print("No se alcanzó la humedad objetivo en el tiempo simulado")

    print(f"Densidad de saturación: {rho_sat:.3f} g/m^3")
    print(f"Masa total inyectada: {masa_in:.3f} g")
    print(f"Masa total condensada: {masa_cond:.3f} g")

    # Gráfico
    HRs = np.array(rhos) / rho_sat * 100.0

    plt.figure()
    plt.plot(np.array(tiempos)*60, HRs)
    plt.axhline(HR_objetivo, linestyle='--')
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Humedad relativa [%]")
    plt.title("Evolución de la Humedad en el Recinto")
    plt.grid(True)
    plt.show()
