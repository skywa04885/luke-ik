"""
Luke's Inverse Kinematics - Demo for automated kitchen, Rien Dumore.
"""

import pygame
from chain import chain_init
from window import Window

if __name__ == '__main__':
    # Initializes the IK Chain.
    chain_init()

    # Creates the window.
    window: Window = Window()
    window.run()

