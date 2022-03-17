"""
Luke's Inverse Kinematics - Demo for automated kitchen, Rien Dumore.
"""

from chain import chain_init
from phy import Phy
from window import Window

if __name__ == '__main__':
    # Prompts the user if we want to use a Phy.
    use_phy: bool = False
    while True:
        data: str = input('Do you want to connect to a PHY? Yes(y) or No(n):')
        if data == 'y':
            use_phy = True
            break
        elif data == 'n':
            break
        else:
            print(f'Invalid input \'{data}\' is not \'y\' or \'n\'')

    # Connects to the phy if needed.
    phy: Phy or None = None
    if use_phy:
        phy = Phy.ask_from_user()

    # Initializes the IK Chain.
    chain_init()

    # Creates the window.
    window: Window = Window(phy=phy)
    window.run()

