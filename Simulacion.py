import simpy
import random
import statistics
import matplotlib.pyplot as plt

# Configuración de la semilla para reproducibilidad
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# Parámetros globales
RAM_CAPACITY = 100  # Capacidad inicial de la RAM
CPU_SPEED = 3       # Instrucciones que el CPU puede procesar por unidad de tiempo
INTERVALO_LLEGADA = 10  # Intervalo de llegada entre procesos

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
            decision = random.randint(1, 21)
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
    cpu = simpy.Resource(env, capacity=1)
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
plt.errorbar(procesos_lista, promedios, yerr=desviaciones, fmt='o-', capsize=5, label="Tiempo promedio")
plt.title("Tiempo promedio vs Número de procesos")
plt.xlabel("Número de procesos")
plt.ylabel("Tiempo promedio en el sistema")
plt.grid(True)
plt.legend()
plt.show()
