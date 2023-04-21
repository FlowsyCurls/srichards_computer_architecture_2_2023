## NOTA


## En plots.py se encuentra el código de graficación para las muestras del ejercicio de análisis.

## Para poder ejecutar los programas debe ubicarse en el directorio en Ubuntu donde los tiene almacenados.
## Para esto, abra un terminal en la localizacion de la carpeta.

##  Utilice los siguientes dos comandos para compilar, enlazar y ejecutar el programa de la cantidad de procesadores en su PC.
gcc processors_quantity.c -o processors_quantity -fopenmp
./processors_quantity

##  Utilice los siguientes dos comandos para compilar, enlazar y ejecutar el programa del ejercicio 1.
gcc saxpi.c -o saxpi -fopenmp
./saxpi

##  Utilice los siguientes dos comandos para compilar, enlazar y ejecutar el programa del ejercicio 2.
gcc euler.c -o euler -fopenmp
./euler


