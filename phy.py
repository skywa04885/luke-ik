from __future__ import annotations
import math
from time import sleep
import serial
import serial.tools.list_ports as list_ports

from bone_vector import bone_vector
from helpers import rad

STEPPER_CONVERSION_DICT = [
    200.0 * 1600.0,    
    -200.0 * 1600.0,
    200.0 * 400.0
]

class Phy:
    def __init__(self, port: str) -> None:
        """Initialzies a new Phy class instance.

        Args:
            port (str): the device path.
        """
        self.ser = serial.Serial(port=port, baudrate=115200)
    
    def move(self, motor: int, theta: float) -> None:
        """Moves the motor to the given angle.

        Args:
            motor (int): The motor index.
            theta (float): The angle.
        """

        # Gets the number of full rotations to perform.
        rotations: float = theta / (math.pi * 2)

        # Calculates the number of pulses.
        pulses: int = int(rotations * STEPPER_CONVERSION_DICT[motor])

        # Writes the target position.
        self.ser.write(f'{motor},{pulses}\n'.encode())

    def write_chain(self, start: bone_vector) -> None:
        """Writes an entire bone chain of values to the PHY.

        Args:
            start (bone_vector): The first bone.
        """

        index: int = 0
        current: bone_vector = start
        while current is not None:
            self.move(index, current.theta)
            index += 1
            current = current.next

    def ask_from_user() -> Phy:
        """Gives the user an list of all devices, and makes him select one.

        Returns:
            Phy: The result PHY.
        """

        # Gets a list of all the comports.
        comports = list_ports.comports()

        # Prints the comports.
        print('Select a COM-Port(Enter the number and press ENTER): ')

        comport_index: int = 0
        for comport in comports:
            print(f'{comport_index}. {comport.name} - {comport.device} - {comport.description}')
            comport_index += 1

        # Gets the user input.
        index: int = 0
        while True:
            # Tries to read the int device index.
            index_str: str = input('Enter device index: ')
            try:
                index: int = int(index_str)
            except:
                print(f'{index_str} is not a valid number!')
                continue

            # Checks if the index is valid.
            if index >= comport_index:
                print(f'The max index is {comport_index - 1}')
                continue
            
            # Exits the prompt.
            break
        
        # Returns the phy.
        return Phy(comports[index].device)