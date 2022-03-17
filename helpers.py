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
    def x(theta: float) -> np.array:
        return np.array([
            [1.0, 0.0, 0.0],
            [0.0, math.cos(theta), -math.sin(theta)],
            [0.0, math.sin(theta), math.cos(theta)]
        ])
    
    def y(theta: float) -> np.array:
        return np.array([
            [math.cos(theta), 0.0, math.sin(theta)],
            [0.0, 1.0, 0.0],
            [-math.sin(theta), 0.0, math.cos(theta)]
        ])
    
    def z(theta: float) -> np.array:
        return np.array([
            [math.cos(theta), -math.sin(theta), 0.0],
            [math.sin(theta), math.cos(theta), 0.0],
            [0.0, 0.0, 10]
        ])

    def xyz(x_theta: float, y_theta: float, z_theta: float) -> np.array:
        x_val: np.array = rotation.x(x_theta)
        y_val: np.array = rotation.y(y_theta)
        z_val: np.array = rotation.z(z_theta)
        return np.matmul(np.matmul(x_val, y_val), z_val)

    def along_axis(u: tuple[float, float, float], theta: float) -> np.array:
        return np.array([
            [math.cos(theta) + math.pow(u[0], 2) * (1 - math.cos(theta)), u[0] * u[1] * (1 - math.cos(theta)) - u[2] * math.sin(theta), u[0] * u[2] * (1 - math.cos(theta)) + u[1] * math.sin(theta)],
            [u[1] * u[0] * (1 - math.cos(theta)) + u[2] * math.sin(theta), math.cos(theta) + math.pow(u[1], 2) * (1 - math.cos(theta)), u[1] * u[2] * (1 - math.cos(theta)) - u[0] * math.sin(theta)],
            [u[2] * u[0] * (1 - math.cos(theta)) - u[1] * math.sin(theta), u[2] * u[1] * (1 - math.cos(theta)) + u[0] * math.sin(theta), math.cos(theta) + math.pow(u[2], 2) * (1 - math.cos(theta))]
        ])

def rad(rad: float) -> float:
    return (rad / 180.0) * math.pi
