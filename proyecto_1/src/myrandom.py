import datetime
import random

# from numpy import linalg
# import numpy as np


# Instruction generator object
class MyRandom:
    def __init__(self):
        # Variables for addresses
        self.addresses = [i for i in range(8)]

        # Variables for instructions
        self.instructions = ["READ", "WRITE", "CALC"]

        # Variables for randint
        self.seed = int(str(datetime.datetime.now().second)[0])
        self.a = 1664525
        self.c = 1013904223
        self.m = 2**32

    """
    Returns the conversion of a decimal integer to a binary string
    """

    def dec_to_bin(self, n):
        # Format an integer as a binary string with leading zeroes
        binary_string = "{0:03b}".format(n)
        return binary_string

    """
    Returns the conversion of a decimal integer to an uppercase hexadeximal string
    """

    def dec_to_hex(self, n):
        # Convert the decimal number to a hex string and remove the '0x' prefix
        hex_str = format(n, "04X")
        return hex_str

    """
    Returns a random float num between 0 and 1
    """

    def random(self):
        m = 2**31 - 1
        a = 16807
        self.seed = (self.seed * a) % m
        return float(self.seed) / m

    """
    Return a number between min and max (both included):
    """

    def randint(self, min, max):
        # Generate the pseudo-random number using the linear congruential equation
        prev_num = self.seed
        self.seed = (self.a * prev_num + self.c) % self.m

        # Transform the generated number into a random number in the desired range
        range = max - min + 1
        num = (self.seed % range) + min

        # Print the generated memory address and random number
        return num

    """
    Variate from a geometric distribution
        n       :   size of the population
        value   :   element to have a success
    
    returns 
        trials  :   number of trials needed to be successful
                    (número de ensayos necesarios para tener un éxito)
    """

    def geometric(self, n, value):
        # initialize counter
        trials = 0

        # keep trying until success or failure
        while True:
            # check if a random integer is equal to the value
            if random.randint(0, n) == value:
                trials += 1
                # exit loop if successful
                break
            trials += 1

        # return total number of attempts to get the value
        return trials

    """
    Returns a random address of the list of adresses
    """

    def _get_random_address(self):
        # X = Number of trials needed to be successful
        X = []
        for address in self.addresses:
            X.append(self.geometric(len(self.addresses), address))
        address = self._get_mean_value_index(X)
        return self.dec_to_bin(address)

    """
    Returns a random number in hex uppercase obtained with randint
    """

    def _get_random_data(self):
        return self.dec_to_hex(self.randint(0, 65535))

    """
    Returns a random instruction between "READ", "WRITE" and "CALC"
    """

    def _get_random_instruction(self):
        # X = Number of trials needed to be successful
        X = []
        n = len(self.instructions)
        for i in range(n):
            X.append(self.geometric(n, i))
        index = X.index(max(X))
        op = self.instructions[index]

        # If the operation is READ, retrieve the address and return it as a list
        if op == "READ":
            address = self._get_random_address()
            return [op, address]

        # If the operation is WRITE, retrieve the address and data, and return them as a list
        if op == "WRITE":
            address = self._get_random_address()
            data = self._get_random_data()
            return [op, address, data]

        # If the operation is neither READ nor WRITE, return the operation as a list
        return [op]

    """
    Returns the index of the mean value of an array
    """

    def _get_mean_value_index(self, arr):
        # Calculate the mean of the array
        mean = sum(arr) / len(arr)

        # Find the index of the value closest to the mean
        return min(range(len(arr)), key=lambda i: abs(arr[i] - mean))

    """
    Set interface StringVar variables a random generated instruction.
    """

    def set_instruction(self, id, StringVar):
        # Get the instruction and unpack its components
        op, *args = self._get_random_instruction()

        # Join the components into a single string using '; ' as a separator
        inst_str = ";".join(map(str, args))

        # Set the instruction string as the value of the next instruction StringVar
        text = f"P{id}: {op} {inst_str}"
        StringVar.set(text)
        # return text


myrandom = MyRandom()
