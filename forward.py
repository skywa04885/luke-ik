import numpy as np

from bone_vector import bone_vector

def fk(end: bone_vector) -> np.array:
    """Performs forward kinematics on the given chain.

    Args:
        end (bone_vector): The last bone of the chain.

    Returns:
        np.array: The FK Position.
    """

    # Initialize stuff.
    end_effector: np.array = np.array([ 0.0, 0.0, 0.0 ])

    # Performs something similar to forward kinematics.
    current: bone_vector or None = end
    while current is not None:
        # Gets the current (not-rotated) end effector position.
        current_end_effector = np.add(end_effector, current.vector())

        # Performs the rotation to the current_end_effector.
        current_end_effector = np.matmul(current.matrix(), current_end_effector)
        
        # Sets the end_effector position to the current end effector position,
        #  and goes to the (next) previous chain element, so we can apply it's
        #  transformations to the current one.
        end_effector = current_end_effector
        current = current.prev

    # Returns the result.
    return end_effector
