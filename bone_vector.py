from __future__ import annotations
import numpy as np

from helpers import rotation

BONE_VECTOR_DIRECTION: np.array = np.array([0.0, 1.0, 0.0])

BONE_TWISTING_ROTATION_AXIS: tuple[float, float, float] = (0.0, 1.0, 0.0)
BONE_TWISTING_VECTOR_DIRECTION: tuple[int, int, int] = (0, 1, 0)

BONE_ROTATIONAL_ROTATION_AXIS: tuple[float, float, float] = (1.0, 0.0, 0.0)
BONE_ROTATIONAL_VECTOR_DIRECTION: tuple[int, int, int] = (0, 1, 0)


class bone_vector:
    def __init__(self, theta: float = 0.0, rotation_axis: tuple[float, float, float] = (0.0, 1.0, 0.0), vector_length: float = 0.0, vector_direction: tuple[float, float, float] = (0, 1, 0), next: bone_vector or None = None, theta_min: float or None = None, theta_max: float or None = None) -> None:
        self.theta = theta
        self.rotation_axis = rotation_axis
        self.vector_length = vector_length
        self.vector_direction = vector_direction
        self.next = next
        self.prev = None
        self.theta_min = theta_min
        self.theta_max = theta_max

        self.matrix_cache = None

    def set_theta(self, theta: float) -> None:
        self.theta = theta
        self.matrix_cache = None

    def vector(self) -> np.array:
        """Generates the untransformed vector of the matrix.

        Returns:
            np.array: The untransformed vector of the matrix.
        """
        return np.array(self.vector_direction) * self.vector_length

    def matrix(self) -> np.array:
        """Generates the rotation matrix of the bone vector.

        Returns:
            np.array: The rotation matrix.
        """
        if self.matrix_cache is not None:
            return self.matrix_cache
        
        self.matrix_cache = rotation.along_axis(self.rotation_axis, self.theta)
        return self.matrix_cache

    def print(self) -> None:
        """Prints the ourselves.
        """
        print(f'bone_vector (theta: {self.theta}, rotation_axis: {self.rotation_axis}, vector_length: {self.vector_length}, vector_direction: {self.vector_direction}, next: {"yes" if self.next is not None else "no"}, prev: {"yes" if self.prev is not None else "no"}, theta_min: {self.theta_min}, theta_max: {self.theta_max} )')

    def link(self) -> None:
        """Links the chain, in this case just gives each joint a reference to the previous joint in the chain.
        """

        prev: bone_vector or None = None
        current: bone_vector or None = self
        while current is not None:
            # Set the previous value of the current.
            current.prev = prev

            # Goes to the next bone, and makes the current previous.
            prev = current
            current = current.next

    def reset_chain(self) -> None:
        temp: bone_vector or None = self
        while temp is not None:
            temp.theta = 0.0
            temp = temp.next

    def print_chain(self) -> None:
        """Prints the entire bone-vector chain from this bone.
        """

        temp: bone_vector or None = self
        while temp is not None:
            temp.print()
            temp = temp.next

    def twisting(theta: float = 0.0, vector_length: float = 0.0, next: bone_vector or None = None, theta_min: float or None = None, theta_max: float or None = None) -> bone_vector:
        """Constructs a twisting joint.

        Args:
            theta (float, optional): The angle. Defaults to 0.0.
            vector_length (float, optional): The vector length. Defaults to 0.0.
            next (bone_vector, optional): The next bone in the chain. Defaults to None.

        Returns:
            bone_vector: The resulting bone.
        """
        return bone_vector(theta=theta, rotation_axis=BONE_TWISTING_ROTATION_AXIS, vector_length=vector_length, vector_direction=BONE_TWISTING_VECTOR_DIRECTION, next=next, theta_min=theta_min, theta_max=theta_max)

    def rotational(theta: float = 0.0, vector_length: float = 0.0, next: bone_vector or None = None, theta_min: float or None = None, theta_max: float or None = None) -> bone_vector:
        """Generates a new rotational vector.

        Args:
            theta (float, optional): The angle. Defaults to 0.0.
            vector_length (float, optional): The vector length. Defaults to 0.0.
            next (bone_vector, optional): The next bone. Defaults to None.

        Returns:
            bone_vector: The resulting vector.
        """
        return bone_vector(theta=theta, rotation_axis=BONE_ROTATIONAL_ROTATION_AXIS, vector_length=vector_length, vector_direction=BONE_ROTATIONAL_VECTOR_DIRECTION, next=next, theta_min=theta_min, theta_max=theta_max)
