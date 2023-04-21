
import matplotlib.pyplot as plt

# pi samples
pi = [0.000006,0.000054,0.000540, 0.002466,0.020307,0.155542,1.290154]
n = [100, 1000, 10000, 100000, 1000000, 10000000, 100000000]
times_ms = [t * 1000 for t in pi]  # Convertir tiempos a milisegundos
plt.plot(times_ms, n)
plt.title('n en función del tiempo de ejecución')
plt.xlabel('Tiempo (ms)')
plt.ylabel('n')
plt.xscale('log')
plt.yscale('log')
plt.show()

# pi_loop samples


# n = [100, 1000, 10000, 100000, 1000000, 10000000, 100000000]
# times = [0.000099, 0.000294, 0.000558, 0.001336, 0.002792, 0.017465, 0.229951]
# times_ms = [t * 1000 for t in times]  # Convertir tiempos a milisegundos
# plt.plot(times_ms, n)
# plt.title('n en función del tiempo de ejecución')
# plt.xlabel('Tiempo (ms)')
# plt.ylabel('n')
# plt.xscale('log')
# plt.yscale('log')
# plt.show()
