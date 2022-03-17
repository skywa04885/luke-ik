import numpy as np
from helpers import rad, generalize_unit


VERSION: str = '0.0.1'
FLOAT_EPSILON: float = 0.00001
DEFAULT_IK_TARGET: np.array = np.array([0.0, 40.0, 0.0])

MOTION_MODE_ARC__START_ANGLE: float = rad(0.0)
MOTION_MODE_ARC__END_ANGLE: float = rad(360.0)
MOTION_MODE_ARC__RADIUS: float = generalize_unit(12, 'mm')
MOTION_MODE_ARC__POSITION: np.array = np.array([ generalize_unit(25.0, 'mm'), generalize_unit(25.0, 'mm'), generalize_unit(25.0, 'mm') ])
MOTION_MODE_ARC__ORIENTATION: list[float] = [rad(-45), 0.0, 0.0]
MOTION_MODE_ARC__PRESCALAR: float = 10.0