import math
import sys
import numpy as np
import pygame
from enum import Enum
from OpenGL.GL import *
from OpenGL.GLU import *
from bone_vector import bone_vector
from defs import FLOAT_EPSILON
from chain import chain_bottom, chain_top


class JoystickButton(Enum):
    Cross = 0
    Circle = 1
    Square = 2
    Triangle = 3
    Share = 4
    Playstation = 5
    Options = 6
    LeftJoyStick = 7
    RightJoyStick = 8
    LeftBack = 9
    RightBack = 10
    ArrowUp = 11
    ArrowDown = 12
    ArrowLeft = 13
    ArrowRight = 14
    Trackpad = 15


class Window:
    def __init__(self, width: int = 512, height: int = 512) -> None:
        self.width = width
        self.height = height

        # Initializes pygame, with the joystick.
        pygame.init()
        pygame.joystick.init()

        # Gets the joystick.
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        # Sets the display mode.
        pygame.display.set_mode(
            (width, height), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.toggle_fullscreen()

        # Configures OpenGL.
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Gets the controller.

        # Initializes the camera state.
        self.camera_rotation = [45, -45, 0]
        self.camera_position = [0, 0, -160]

        # Initializes the button state.
        self.left_key_pressed = False
        self.right_key_pressed = False
        self.up_key_pressed = False
        self.down_key_pressed = False

        # Initializes the IK state.
        self.ik_target: np.array = np.array([0.0, 40.0, 0.0])

        # Initializes the joystick stuff.
        self.axis_data = {
            0: 0.0,
            1: 0.0,
            2: 0.0,
            3: 0.0,
            4: 0.0,
            5: 0.0,
        }

    def handle_joystick_button_down(self, button: JoystickButton) -> None:
        pass

    def handle_joystick_button_up(self, button: JoystickButton) -> None:
        pass

    def handle_key_down(self, event: pygame.event) -> None:
        # Arrow Keys
        if event.key == pygame.K_LEFT:
            self.left_key_pressed = True
            return
        elif event.key == pygame.K_RIGHT:
            self.right_key_pressed = True
            return
        elif event.key == pygame.K_UP:
            self.up_key_pressed = True
            return
        elif event.key == pygame.K_DOWN:
            self.down_key_pressed = True
            return
        elif event.key == pygame.K_q:
            sys.exit(0)

    def handle_key_up(self, event: pygame.event) -> None:
        # Arrow Keys
        if event.key == pygame.K_LEFT:
            self.left_key_pressed = False
            return
        elif event.key == pygame.K_RIGHT:
            self.right_key_pressed = False
            return
        elif event.key == pygame.K_UP:
            self.up_key_pressed = False
            return
        elif event.key == pygame.K_DOWN:
            self.down_key_pressed = False
            return

    def handle_mousewheel(self, event: pygame.event) -> None:
        self.camera_position[2] += event.y

    def handle_window_resize(self, event: pygame.event) -> None:
        self.width = event.x
        self.height = event.y

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self.handle_key_down(event)
            elif event.type == pygame.KEYUP:
                self.handle_key_up(event)
            elif event.type == pygame.MOUSEWHEEL:
                self.handle_mousewheel(event)
            elif event.type == pygame.JOYBUTTONDOWN:
                self.handle_joystick_button_down(JoystickButton(event.button))
            elif event.type == pygame.JOYBUTTONUP:
                self.handle_joystick_button_up(JoystickButton(event.button))
            elif event.type == pygame.JOYAXISMOTION:
                self.axis_data[event.axis] = math.floor(
                    event.value * 100.0) / 100.0
            elif event.type == pygame.WINDOWRESIZED:
                self.handle_window_resize(event)

    def set_color(self, r: float, g: float, b: float, a=1.0) -> None:
        glColor4f(r, g, b, a)

    def draw_chain(self, start: bone_vector, end: bone_vector) -> None:
        # Initialize stuff.
        end_effector: np.array = np.array([0.0, 0.0, 0.0])

        # Contains an array of points which will be the end-points of the joints.
        lines = []

        # Performs something similar to forward kinematics.
        current: bone_vector or None = end
        while current is not None:
            # Gets the current (not-rotated) end effector position.
            current_end_effector = np.add(end_effector, current.vector())

            # Performs the rotation to the current_end_effector.
            current_end_effector = np.matmul(
                current.matrix(), current_end_effector)

            # Performs some requirements for the visualization.
            for i in range(0, len(lines)):
                lines[i] = np.add(lines[i], current.vector())
                lines[i] = np.matmul(current.matrix(), lines[i])
            lines.append(np.matmul(current.matrix(), current.vector()))

            # Sets the end_effector position to the current end effector position,
            #  and goes to the (next) previous chain element, so we can apply it's
            #  transformations to the current one.
            end_effector = current_end_effector
            current = current.prev

        # Adds the origin.
        lines.append(np.array([0, 0, 0]))

        # Draws the lines.
        for i in range(0, len(lines) - 1):
            self.set_color(1.0, 1.0, 1.0)
            self.draw_dot(lines[i + 1], 5)
            self.set_color(1.0, 0.5, 1.0)
            self.draw_line(lines[i], lines[i + 1], dotted=True)

        # Draws a dotted line to the end effector.
        self.set_color(1.0, 0.5, 0.5)
        self.draw_line([0, 0, 0], end_effector, dotted=True)

        # Draws the end effector dot.
        self.set_color(1.0, 0.5, 0.5)
        self.draw_dot(end_effector)

    def draw_dot(self, position: np.array = np.array([0.0, 0.0, 0.0]), size: float = 20) -> None:
        # Sets the point size.
        glPointSize(size)

        # Draws the point.
        glBegin(GL_POINTS)
        glVertex3f(position[0], position[1], position[2])
        glEnd()

    def draw_line(self, start: any, end: any, width=10.0, dotted=False) -> None:
        # Checks if we need to enable line stippling.
        if dotted:
            glEnable(GL_LINE_STIPPLE)
            glLineStipple(1, 0x0101)

        # Sets the line width.
        glLineWidth(width)

        # Draws the line.
        glBegin(GL_LINES)
        glVertex3f(start[0], start[1], start[2])
        glVertex3f(end[0], end[1], end[2])
        glEnd()

        # Disable stippling.
        if dotted:
            glDisable(GL_LINE_STIPPLE)

    def draw_axis(self, position: np.array = np.array([0, 0, 0]), size: float = 5.0) -> None:
        # X
        self.set_color(1.0, 0.0, 0.0, 0.7)
        self.draw_line(position, np.add(position, [size, 0.0, 0.0]), 4)

        # Y
        self.set_color(0.0, 1.0, 0.0, 0.7)
        self.draw_line(position, np.add(position, [0.0, size, 0.0]), 4)

        # Z
        self.set_color(0.0, 0.0, 1.0, 0.7)
        self.draw_line(position, np.add(position, [0.0, 0.0, size]), 4)

    def render_camera(self) -> None:
        # Sets the matrix mode to the projection matrix, and loads the identity matrix.
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        # Generates the perspective matrix.
        gluPerspective(45, (self.width / self.height), 0.1, 500.0)

        # Performs some camera transformations.
        glTranslatef(
            self.camera_position[0], self.camera_position[1], self.camera_position[2])
        glRotatef(self.camera_rotation[0], 1.0, 0.0, 0.0)
        glRotatef(self.camera_rotation[1], 0.0, 1.0, 0.0)
        glRotatef(self.camera_rotation[2], 0.0, 0.0, 1.0)

    def clear_screen(self) -> None:
        glClearColor(0.1, 0.1, 0.1, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def render(self) -> None:
        self.clear_screen()
        self.render_camera()
        self.draw_axis(size=10)

        # Draws the IK Target.
        self.set_color(0.2, 1.0, 0.2, 0.9)
        self.draw_dot(position=self.ik_target, size=10)
        self.draw_chain(chain_bottom, chain_top)

    def update_ik_target(self, new_target: np.array) -> None:
        # Sets the new target.
        self.ik_target = new_target

        # Performs the IK Solving.

    def run(self) -> None:
        while True:
            # Handles the events.
            self.handle_events()

            # Does something with the keys.
            if self.left_key_pressed:
                self.camera_rotation[1] += 0.8
            if self.right_key_pressed:
                self.camera_rotation[1] -= 0.8
            if self.up_key_pressed:
                self.camera_rotation[0] += 0.8
            if self.down_key_pressed:
                self.camera_rotation[0] -= 0.8

            # Does something with the axis data.
            if abs(self.axis_data[0]) > 0.1:
                self.update_ik_target(
                    np.add(self.ik_target, [self.axis_data[0] / 4.0, 0.0, 0.0]))
            if abs(self.axis_data[1]) > 0.1:
                self.update_ik_target(
                    np.add(self.ik_target, [0.0, 0.0, self.axis_data[1] / 4.0]))
            if abs(self.axis_data[3]) > 0.1:
                self.update_ik_target(
                    np.add(self.ik_target, [0.0, self.axis_data[3] / 4.0, 0.0]))

            # Renders.
            self.render()

            # Swaps the buffers.
            pygame.display.flip()
            pygame.time.wait(10)
