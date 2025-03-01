"""
Universidad del Valle de Guatemala
Departamento de Ciencia de la Computación
Curso: Algoritmos y Estructuras de Datos 
Proyecto: Hoja de Trabajo #5
Autores:
- Denil José Parada Cabrera - 24761
- Hugo Méndez - 241265
- Andrés Ismalej - 24005
Fecha: 27/02/2025
Descripción: Programa de simulación de procesos de una CPU.
"""

import simpy
import random
import statistics
import matplotlib.pyplot as plt

# Configuración de la semilla para reproducibilidad
random.seed(42)

# Parámetros globales
RAM_CAPACITY = 100  # Capacidad inicial de la RAM
CPU_SPEED = 3       # Instrucciones que el CPU puede procesar por unidad de tiempo
INTERVALO_LLEGADA = 1  # Intervalo de llegada entre procesos

# Proceso simulado
def proceso(env, nombre, ram, cpu, tiempo_llegada, resultados):
    # Tiempo en que el proceso llega
    yield env.timeout(tiempo_llegada)

    llegada = env.now
    memoria_requerida = random.randint(1, 10)
    instrucciones = random.randint(1, 10)

    # Solicitar memoria RAM
    yield ram.get(memoria_requerida)

    # Proceso listo para usar el CPU
    while instrucciones > 0:
        with cpu.request() as req:
            yield req  # Esperar turno en la cola del CPU
            instrucciones_a_ejecutar = min(instrucciones, CPU_SPEED)
            yield env.timeout(1)  # Tiempo que toma ejecutar instrucciones
            instrucciones -= instrucciones_a_ejecutar

            # Simular operaciones de I/O o volver a la cola ready
            decision = random.randint(1, 2**1)

            if instrucciones > 0 and decision == 1:
                yield env.timeout(random.uniform(0.5, 2))  # Operaciones I/O

    # Devolver memoria RAM utilizada
    yield ram.put(memoria_requerida)
    resultados.append(env.now - llegada)

# Simulación completa
def correr_simulacion(numero_procesos, ram_capacidad, cpu_speed, intervalo_llegada):
    global CPU_SPEED
    CPU_SPEED = cpu_speed  # Actualizar la velocidad del CPU

    env = simpy.Environment()
    ram = simpy.Container(env, init=ram_capacidad, capacity=ram_capacidad)
    cpu = simpy.Resource(env, capacity=1) # Se permite variar el número de CPU'S
    resultados = []

    for i in range(numero_procesos):
        tiempo_llegada = random.expovariate(1.0 / intervalo_llegada)
        env.process(proceso(env, f"Proceso {i+1}", ram, cpu, tiempo_llegada, resultados))

    env.run()

    promedio = statistics.mean(resultados)
    desviacion = statistics.stdev(resultados) if len(resultados) > 1 else 0

    return promedio, desviacion

# Ejecutar simulaciones con diferentes cantidades de procesos y graficar
procesos_lista = [25, 50, 100, 150, 200]
promedios = []
desviaciones = []

for procesos in procesos_lista:
    promedio, desviacion = correr_simulacion(procesos, RAM_CAPACITY, CPU_SPEED, INTERVALO_LLEGADA)
    promedios.append(promedio)
    desviaciones.append(desviacion)

# Graficar resultados
plt.figure(figsize=(10, 6))
plt.errorbar(promedios, procesos_lista, yerr=desviaciones, fmt='o-', capsize=5, label="Número de procesos")

# Agregar etiquetas con el promedio y la desviación estándar en cada punto
for i in range(len(procesos_lista)):
    plt.text(promedios[i], procesos_lista[i], f"{promedios[i]:.2f} ± {desviaciones[i]:.2f}", 
             ha='right', va='bottom', fontsize=10, color='blue')

plt.title("Número de procesos vs Tiempo promedio")
plt.xlabel("Tiempo promedio en el sistema")
plt.ylabel("Número de procesos")
plt.grid(True)
plt.legend()
plt.show()
