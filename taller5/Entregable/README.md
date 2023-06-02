* **Para compilar y ejecutar el programa sobel_serial.c:**

```
	gcc -o sobel_serial sobel_serial.c -lm
	./sobel_serial
```

* **Para compilar y ejecutar el programa sobel_serial.c:**

```
	mpicc -o sobel_parallel sobel_parallel.c -lm
	mpirun -np 4 ./sobel_parallel
```
