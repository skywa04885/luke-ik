import numpy as np
from bone_vector import bone_vector
from forward import fk
from helpers import bounded_theta


def ik(start_bone: bone_vector, end_bone: bone_vector, target: np.array, max_it: int = 100, epsilon: float = 0.1, eta: float = 0.1) -> float:
    error: float = np.linalg.norm(target - fk(end_bone))

    for i in range(0, max_it):
        moved: bool = False

        # Loops over the bones and tweaks the parameters.
        current: bone_vector = start_bone
        while current is not None:
            # Stores the original theta for possible restoration.
            original_theta = current.theta

            # Tries if incrementing or decrementing reduces the error
            #  if both reduce pick the largest reduction, if both increase
            #  just keep the original value.
            error_original = error
            current.set_theta(bounded_theta(original_theta + eta, current.theta_min, current.theta_max))
            error_incrementation = np.linalg.norm(target - fk(end_bone))
            current.set_theta(bounded_theta(original_theta - eta, current.theta_min, current.theta_max))
            error_decrementation = np.linalg.norm(target - fk(end_bone))

            # Checks which error is the best and what change to keep.
            if error_incrementation > error_original and error_decrementation > error_original:
                current.set_theta(original_theta)
                error = (error_incrementation + error_decrementation) / 2
                moved = True
            elif error_incrementation < error_decrementation:
                current.set_theta(original_theta + eta)
                error = error_incrementation
                moved = True
            elif error_decrementation < error_incrementation:
                current.set_theta(original_theta - eta)
                error = error_decrementation
                moved = True

            # Checks if we should break.
            if error < epsilon:
                return error

            eta = error / 100

            # Goes to the next joint.
            current = current.next
        
        if not moved:
            return error
