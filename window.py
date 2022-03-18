import math
import sys
from time import time
import numpy as np
import pygame
from enum import Enum
from OpenGL.GL import *
from OpenGL.GLU import *
from bone_vector import bone_vector
from defs import DEFAULT_IK_TARGET, FLOAT_EPSILON, MOTION_MODE_ARC__END_ANGLE, MOTION_MODE_ARC__ORIENTATION, MOTION_MODE_ARC__POSITION, MOTION_MODE_ARC__PRESCALAR, MOTION_MODE_ARC__RADIUS, MOTION_MODE_ARC__START_ANGLE
from chain import chain_bottom, chain_top
from helpers import rad, rotation
from inverse import ik
from phy import Phy


class MotionMode(Enum):
    Manual = 0
    Arc = 1


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
    def __init__(self, width: int = 512, height: int = 512, phy: Phy or None = None) -> None:
        self.width = width
        self.height = height
        self.phy = phy

        # Initializes pygame, with the joystick.
        pygame.init()
        pygame.joystick.init()

        # Gets the joystick.
        self.joystick: pygame.joystick.Joystick or None = None
        if pygame.joystick.get_count() > 0:
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

        # Initializes the camera state.
        self.camera_rotation = [45, -45, 0]
        self.camera_position = [0, 0, -160]

        # Initializes the button state.
        self.left_key_pressed = False
        self.right_key_pressed = False
        self.up_key_pressed = False
        self.down_key_pressed = False

        # Initializes the IK state.
        self.ik_target: np.array = DEFAULT_IK_TARGET
        self.ik_had_previous_large_error = False
        self.motion_mode = MotionMode.Arc

        # Initializes the joystick stuff.
        self.joystick_left_arrow_pressed = False
        self.joystick_right_arrow_pressed = False
        self.joystick_up_arrow_pressed = False
        self.joystick_down_arrow_pressed = False
        self.joystick_back_left_pressed = False
        self.joystick_back_right_pressed = False
        self.joystick_left_stick_pressed = False
        self.joystick_right_stick_pressed = False
        self.axis_data = {
            0: 0.0,
            1: 0.0,
            2: 0.0,
            3: 0.0,
            4: 0.0,
            5: 0.0,
        }

        # Arc motion options.
        self.arc_start: float = MOTION_MODE_ARC__START_ANGLE
        self.arc_end: float = MOTION_MODE_ARC__END_ANGLE
        self.arc_radius: float = MOTION_MODE_ARC__RADIUS
        self.arc_position: np.array = MOTION_MODE_ARC__POSITION
        self.arc_orientation: list[float] = MOTION_MODE_ARC__ORIENTATION

    def handle_joystick_button_down(self, button: JoystickButton) -> None:
        if button == JoystickButton.Cross:
            # Resets the chain.
            chain_bottom.reset_chain()

            # Recomputes.
            self.solve_ik_target()
            return
        elif button == JoystickButton.Circle:
            # Sets the default target.
            self.update_ik_target(DEFAULT_IK_TARGET)
            return
        elif button == JoystickButton.ArrowLeft:
            self.joystick_left_arrow_pressed = True
            return
        elif button == JoystickButton.ArrowRight:
            self.joystick_right_arrow_pressed = True
            return
        elif button == JoystickButton.ArrowUp:
            self.joystick_up_arrow_pressed = True
            return
        elif button == JoystickButton.ArrowDown:
            self.joystick_down_arrow_pressed = True
            return
        elif button == JoystickButton.LeftBack:
            self.joystick_back_left_pressed = True
            return
        elif button == JoystickButton.RightBack:
            self.joystick_back_right_pressed = True
            return
        elif button == JoystickButton.Options:
            if self.motion_mode == MotionMode.Manual:
                self.motion_mode = MotionMode.Arc
            elif self.motion_mode == MotionMode.Arc:
                self.motion_mode = MotionMode.Manual
            print(f'Changed motion mode to {self.motion_mode}')
        elif button == JoystickButton.LeftJoyStick:
            self.joystick_left_stick_pressed = True
            return
        elif button == JoystickButton.RightJoyStick:
            self.joystick_right_stick_pressed = True
            return

    def handle_joystick_button_up(self, button: JoystickButton) -> None:
        if button == JoystickButton.ArrowLeft:
            self.joystick_left_arrow_pressed = False
            return
        elif button == JoystickButton.ArrowRight:
            self.joystick_right_arrow_pressed = False
            return
        elif button == JoystickButton.ArrowUp:
            self.joystick_up_arrow_pressed = False
            return
        elif button == JoystickButton.ArrowDown:
            self.joystick_down_arrow_pressed = False
            return
        elif button == JoystickButton.LeftBack:
            self.joystick_back_left_pressed = False
            return
        elif button == JoystickButton.RightBack:
            self.joystick_back_right_pressed = False
            return
        elif button == JoystickButton.LeftJoyStick:
            self.joystick_left_stick_pressed = False
            return
        elif button == JoystickButton.RightJoyStick:
            self.joystick_right_stick_pressed = False
            return

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

    def draw_arc(self, position: np.array = np.array([ 0.0, 0.0, 0.0 ]), transform: np.array = np.identity(3), radius: float = 1.0, width: float = 5.0, start: float = 0.0, end: float = 2 * math.pi) -> None:
        # Sets the line width.
        glLineWidth(width)

        # Starts drawing the lines.
        glBegin(GL_LINES)
        steps: int = int((abs(end - start) / math.pi) * 30)
        for i in range(0, steps):
            angle: float = start + ((end - start) / float(steps)) * i
            vertex_x, vertex_y = math.cos(angle) * radius, math.sin(angle) * radius
            vertex_position = np.matmul(
                transform, np.array([vertex_x, vertex_y, 0.0]))
            vertex_position = np.add(vertex_position, position)
            glVertex3f(vertex_position[0], vertex_position[1], vertex_position[2])

        glEnd()

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
            self.draw_dot(lines[i], 5)
            self.set_color(1.0, 0.5, 1.0)
            self.draw_line(lines[i], lines[i + 1], dotted=True)

        # Draws a dotted line to the end effector.
        self.set_color(1.0, 0.5, 0.5)
        self.draw_line([0, 0, 0], end_effector, dotted=True)

        # Dras the axis.
        self.draw_axis(position=end_effector, size=5.0)

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

    def draw_axis(self, position: np.array = np.array([0, 0, 0]), size: float = 5.0, width: float = 2.0) -> None:
        # X
        self.set_color(1.0, 0.0, 0.0, 0.7)
        self.draw_line(position, np.add(position, [size, 0.0, 0.0]), width)

        # Y
        self.set_color(0.0, 1.0, 0.0, 0.7)
        self.draw_line(position, np.add(position, [0.0, size, 0.0]), width)

        # Z
        self.set_color(0.0, 0.0, 1.0, 0.7)
        self.draw_line(position, np.add(position, [0.0, 0.0, size]), width)

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
        # Clears the screen.
        self.clear_screen()

        # Renders the camera.
        self.render_camera()
        self.draw_axis(size=30)

        # Draws the IK Target.
        self.set_color(0.2, 1.0, 0.2, 0.9)
        self.draw_dot(position=self.ik_target, size=10)
        self.draw_chain(chain_bottom, chain_top)

        # Renders the arc.
        if self.motion_mode == MotionMode.Arc:
            self.set_color(1.0, 1.0, 1.0, 0.7)
            self.draw_arc(
                position=self.arc_position,
                transform=rotation.xyz(self.arc_orientation[0], self.arc_orientation[1], self.arc_orientation[2]),
                radius=self.arc_radius,
                start=self.arc_start,
                end=self.arc_end
            )

    def update_ik_target(self, new_target: np.array) -> None:
        # Sets the new target.
        self.ik_target = new_target

        # Solves the target.
        self.solve_ik_target()

    def solve_ik_target(self) -> None:
        # Performs the IK Solving.
        start_time = time()
        error: float = ik(start_bone=chain_bottom, end_bone=chain_top, target=self.ik_target)
        end_time = time()
        print(f'Solved new IK target with error: {error} in {end_time - start_time}')

        # Vibrates if the error is large
        if error == None or error > 1.0:
            if not self.ik_had_previous_large_error:
                self.ik_had_previous_large_error = True
                if self.joystick is not None:
                    self.joystick.rumble(60.0, 70.0, 100)
        else:
            self.ik_had_previous_large_error = False
        
        # Updates the Phy.
        if self.phy is not None:
            self.phy.write_chain(chain_bottom)

    def run(self) -> None:
        # Initial target solve.
        self.solve_ik_target()

        # Event loop.
        while True:
            # Handles the events.
            self.handle_events()

            # Performs camera rotations
            if self.left_key_pressed or self.joystick_left_arrow_pressed:
                self.camera_rotation[1] += 0.8
            if self.right_key_pressed or self.joystick_right_arrow_pressed:
                self.camera_rotation[1] -= 0.8
            if self.up_key_pressed or self.joystick_up_arrow_pressed:
                self.camera_rotation[0] += 0.8
            if self.down_key_pressed or self.joystick_down_arrow_pressed:
                self.camera_rotation[0] -= 0.8
            
            # Zooms in and out.
            if self.joystick_back_right_pressed:
                self.camera_position[2] += 0.5
            if self.joystick_back_left_pressed:
                self.camera_position[2] -= 0.5

            # Checks how to Interpret the inputs.
            if self.motion_mode == MotionMode.Manual:
                # Does something with the axis data.
                if abs(self.axis_data[0]) > 0.1:
                    self.update_ik_target(
                        np.add(self.ik_target, [self.axis_data[0] / 4.0, 0.0, 0.0]))
                if abs(self.axis_data[1]) > 0.1:
                    self.update_ik_target(
                        np.add(self.ik_target, [0.0, 0.0, self.axis_data[1] / 4.0]))
                if abs(self.axis_data[3]) > 0.1:
                    self.update_ik_target(
                        np.add(self.ik_target, [0.0, - self.axis_data[3] / 4.0, 0.0]))
            elif self.motion_mode == MotionMode.Arc:
                arc_modified: bool = False

                # Checks if we need to modify shit.
                if self.joystick_left_stick_pressed:
                    if abs(self.axis_data[0]) > 0.1:
                        self.arc_orientation[1] += self.axis_data[0] / 40.0
                        arc_modified = True
                    if abs(self.axis_data[1]) > 0.1:
                        self.arc_orientation[0] += self.axis_data[1] / 40.0
                        arc_modified = True
                else:
                    if abs(self.axis_data[0]) > 0.1:
                        self.arc_position = np.add(self.arc_position, [self.axis_data[0] / 4.0, 0.0, 0.0])
                        arc_modified = True
                    if abs(self.axis_data[1]) > 0.1:
                        self.arc_position = np.add(self.arc_position, [0.0, 0.0, self.axis_data[1] / 4.0])
                        arc_modified = True
                
                if self.joystick_right_stick_pressed:
                    if abs(self.axis_data[2]) > 0.1:
                        self.arc_radius += self.axis_data[2]
                        arc_modified = True
                else:
                    if abs(self.axis_data[3]) > 0.1:
                        self.arc_position = np.add(self.arc_position, [0.0, - self.axis_data[3] / 4.0, 0.0])
                        arc_modified = True

                if self.axis_data[4] > 0.4:
                    self.arc_start -= rad(self.axis_data[4] / 2.0)
                    if self.arc_start < rad(0.0):
                        self.arc_start = rad(0.0)
                    arc_modified = True
                
                if self.axis_data[5] > 0.4:
                    self.arc_start += rad(self.axis_data[5] / 2.0)
                    if self.arc_start > rad(360.0):
                        self.arc_start = rad(360.0)
                    arc_modified = True

                if not arc_modified:
                    # Clamps the time between two values.
                    delta: float = abs(self.arc_end - self.arc_start)
                    t: float = time() / ((MOTION_MODE_ARC__PRESCALAR / (math.pi * 2)) * delta)
                    clamped: float = t % 2 * delta
                    
                    # Determines the angle, moves forward and backwards.
                    angle: float = 0.0
                    if clamped <= delta:
                        angle = self.arc_start + clamped
                    elif clamped > delta:
                        angle = self.arc_end - clamped - self.arc_start

                    # Performs the computation.
                    x: float = math.cos(angle) * self.arc_radius
                    y: float = math.sin(angle) * self.arc_radius
                    target: np.array = np.matmul(rotation.xyz(self.arc_orientation[0], self.arc_orientation[1], self.arc_orientation[2]), np.array([ x, y, 0.0 ]))
                    target = np.add(self.arc_position, target)
                    self.update_ik_target(target)

            # Renders.
            self.render()

            # Swaps the buffers.
            pygame.display.flip()
            pygame.time.wait(10)
