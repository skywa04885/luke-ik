import math
import numpy as np

GENERALIZE_UNIT_MULTIPLIERS = {
    'um': 1.0 / 1000.0,
    'mm': 1.0,
    'cm': 10.0,
    'm': 1000.0
}

def bounded_theta(theta: float, theta_min: float or None, theta_max: float or None) -> float:
    if theta_min is None or theta_max is None:
        return theta
    elif theta >= theta_min and theta <= theta_max:
        return theta
    elif theta < theta_min:
        return theta_min
    elif theta > theta_max:
        return theta_max

def generalize_unit(value: float, unit: str):
    multiplier: float = GENERALIZE_UNIT_MULTIPLIERS[unit]
    return value * multiplier

class rotation:
    # def x(theta: float) -> np.array:
    #     return np.array([
    #         [,,],
    #         [,,],
    #         [,,]
    #     ])
    
    # def y(theta: float) -> np.array:
    #     return np.array([
    #         [,,],
    #         [,,],
    #         [,,]
    #     ])
    
    # def z(theta: float) -> np.array:
    #     return np.array([
    #         [,,],
    #         [,,],
    #         [,,]
    #     ])


    def along_axis(u: tuple[float, float, float], theta: float) -> np.array:
        return np.array([
            [math.cos(theta) + math.pow(u[0], 2) * (1 - math.cos(theta)), u[0] * u[1] * (1 - math.cos(theta)) - u[2] * math.sin(theta), u[0] * u[2] * (1 - math.cos(theta)) + u[1] * math.sin(theta)],
            [u[1] * u[0] * (1 - math.cos(theta)) + u[2] * math.sin(theta), math.cos(theta) + math.pow(u[1], 2) * (1 - math.cos(theta)), u[1] * u[2] * (1 - math.cos(theta)) - u[0] * math.sin(theta)],
            [u[2] * u[0] * (1 - math.cos(theta)) - u[1] * math.sin(theta), u[2] * u[1] * (1 - math.cos(theta)) + u[0] * math.sin(theta), math.cos(theta) + math.pow(u[2], 2) * (1 - math.cos(theta))]
        ])

def rad(rad: float) -> float:
    return (rad / 180.0) * math.pi
