# Flags
CC=gcc
CFLAGS=-msse -msse4.1 -lrt -lm -w

# Paths
BIN_DIR=bin
SRC_DIR=src

# Create bin directory if it does not exist
$(shell mkdir -p $(BIN_DIR))

all: ejercicio1 ejercicio2


helloworld: helloWorld.c
	$(CC) $(CFLAGS) -o $(BIN_DIR)/$@ $<
	./$(BIN_DIR)/$@

ejercicio1: $(SRC_DIR)/ejercicio1.c
	$(CC) $(CFLAGS) -o $(BIN_DIR)/$@ $<
	./$(BIN_DIR)/$@

ejercicio2: $(SRC_DIR)/ejercicio2.c
	$(CC) $(CFLAGS) -o $(BIN_DIR)/$@ $<
	./$(BIN_DIR)/$@

clean:
	rm -rf $(BIN_DIR)

.PHONY: clean
