import math
import glfw
from matplotlib.pyplot import bone
import numpy as np
import random
import serial.tools.list_ports
import time
from enum import Enum
from OpenGL.GL import *
from OpenGL.GLU import *
from bone_vector import bone_vector
from forward import fk
from helpers import generalize_unit, rad, rotation
from inverse import ik
from phy import Phy


class VisualizerMode(Enum):
    USER = 0
    RANDOM = 1
    CIRCULAR = 2


WINDOW_WIDTH: int = 1024
WINDOW_HEIGHT: int = 1024
WINDOW_TITLE: str = 'LukeIK'


g_key_w_hold: bool = False
g_key_a_hold: bool = False
g_key_s_hold: bool = False
g_key_d_hold: bool = False
g_key_space_hold: bool = False
g_key_shift_hold: bool = False
g_key_left_arrow_hold: bool = False
g_key_right_arrow_hold: bool = False
g_key_top_arrow_hold: bool = False
g_key_bottom_arrow_hold: bool = False
g_key_tab_hold: bool = False
g_key_right_shift_hold: bool = False

g_camera_position: list[float, float, float] = [0, 0, -80]
g_camera_rotation: list[float, float, float] = [45, -45, 0]

g_vis_mode: VisualizerMode = VisualizerMode.USER
g_ik_target: np.array = np.array([0, 73.0, 0])
g_ik_target_range_start: float = -15.0
g_ik_target_range_end: float = 15.0
g_last_random_ik_target: float = 0.0
g_circle_radius: float = 30.0
g_solve_interval: float = 0.5

phy: Phy = Phy.ask_from_user()

def generate_random_ik_target() -> None:
    g_ik_target[0] = random.randrange(
        g_ik_target_range_start, g_ik_target_range_end)
    g_ik_target[1] = random.randrange(
        g_ik_target_range_start, g_ik_target_range_end)
    g_ik_target[2] = random.randrange(
        g_ik_target_range_start, g_ik_target_range_end)


# Creates the bones for the chain.
bone_top = bone_vector.rotational(
    vector_length=generalize_unit(34.0, 'mm'), theta=rad(0), theta_min=rad(-120), theta_max=rad(120))
bone_middle = bone_vector.rotational(
    vector_length=generalize_unit(30.5, 'mm'), next=bone_top, theta=rad(0), theta_min=rad(-90), theta_max=rad(90))
bone_bottom = bone_vector.twisting(
    theta=rad(0.0),
    vector_length=generalize_unit(0, 'mm'),
    next=bone_middle,
    theta_min=rad(-180.0),
    theta_max=rad(180.0)
)

# Links the chain.
bone_bottom.link()


def keypress(window, key, scancode, action, mods):
    global g_key_w_hold
    global g_key_a_hold
    global g_key_s_hold
    global g_key_d_hold
    global g_key_space_hold
    global g_key_shift_hold
    global g_key_left_arrow_hold
    global g_key_right_arrow_hold
    global g_key_top_arrow_hold
    global g_solve_interval
    global g_key_bottom_arrow_hold
    global g_perform_random_ik
    global g_key_tab_hold
    global g_key_right_shift_hold
    global g_vis_mode
    global g_circle_radius

    if key == glfw.KEY_U:
        if g_vis_mode == VisualizerMode.RANDOM:
            g_solve_interval += 0.01
        elif g_vis_mode == VisualizerMode.CIRCULAR:
            g_circle_radius += 0.5
    elif key == glfw.KEY_J:
        if g_vis_mode == VisualizerMode.RANDOM:
            g_solve_interval -= 0.01
        elif g_vis_mode == VisualizerMode.CIRCULAR:
            g_circle_radius -= 0.5

    if action == glfw.PRESS:
        if key == glfw.KEY_Q:
            bone_bottom.reset_chain()
            phy.write_chain(bone_bottom)

            glfw.set_window_should_close(window, True)
        elif key == glfw.KEY_W:
            g_key_w_hold = True
        elif key == glfw.KEY_A:
            g_key_a_hold = True
        elif key == glfw.KEY_S:
            g_key_s_hold = True
        elif key == glfw.KEY_D:
            g_key_d_hold = True
        elif key == glfw.KEY_SPACE:
            g_key_space_hold = True
        elif key == glfw.KEY_LEFT_SHIFT:
            g_key_shift_hold = True
        elif key == glfw.KEY_LEFT:
            g_key_left_arrow_hold = True
        elif key == glfw.KEY_RIGHT:
            g_key_right_arrow_hold = True
        elif key == glfw.KEY_UP:
            g_key_top_arrow_hold = True
        elif key == glfw.KEY_DOWN:
            g_key_bottom_arrow_hold = True
        elif key == glfw.KEY_TAB:
            g_key_tab_hold = True
        elif key == glfw.KEY_RIGHT_SHIFT:
            g_key_right_shift_hold = True
        elif key == glfw.KEY_M:
            if g_vis_mode == VisualizerMode.USER:
                g_vis_mode = VisualizerMode.RANDOM
            elif g_vis_mode == VisualizerMode.RANDOM:
                g_vis_mode = VisualizerMode.CIRCULAR
            elif g_vis_mode == VisualizerMode.CIRCULAR:
                g_vis_mode = VisualizerMode.USER
    elif action == glfw.RELEASE:
        if key == glfw.KEY_W:
            g_key_w_hold = False
        elif key == glfw.KEY_A:
            g_key_a_hold = False
        elif key == glfw.KEY_S:
            g_key_s_hold = False
        elif key == glfw.KEY_D:
            g_key_d_hold = False
        elif key == glfw.KEY_SPACE:
            g_key_space_hold = False
        elif key == glfw.KEY_LEFT_SHIFT:
            g_key_shift_hold = False
        elif key == glfw.KEY_LEFT:
            g_key_left_arrow_hold = False
        elif key == glfw.KEY_RIGHT:
            g_key_right_arrow_hold = False
        elif key == glfw.KEY_UP:
            g_key_top_arrow_hold = False
        elif key == glfw.KEY_DOWN:
            g_key_bottom_arrow_hold = False
        elif key == glfw.KEY_TAB:
            g_key_tab_hold = False
        elif key == glfw.KEY_RIGHT_SHIFT:
            g_key_right_shift_hold = False


def draw_dot(pos: np.array, size: float = 20) -> None:
    glPointSize(size)
    glBegin(GL_POINTS)
    glVertex3f(pos[0], pos[1], pos[2])
    glEnd()


def draw_circle(position: np.array, transform: np.array, radius: float = 1.0, width: float = 5.0) -> None:
    glLineWidth(width)
    glBegin(GL_LINES)
    prev = None
    for i in range(0, 100):
        angle: float = (math.pi / 50.0) * float(i)
        vertex_x, vertex_y = math.cos(angle) * radius, math.sin(angle) * radius
        vertex_position = np.matmul(
            transform, np.array([vertex_x, vertex_y, 0.0]))
        vertex_position = np.add(vertex_position, position)
        glVertex3f(vertex_position[0], vertex_position[1], vertex_position[2])

    glEnd()


def draw_chain(start: bone_vector, end: bone_vector) -> None:
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
        glColor3f(1.0, 1.0, 1.0)
        draw_dot(lines[i + 1], 5)
        glColor3f(1.0, 0.5, 1.0)
        draw_line(lines[i], lines[i + 1], dotted=True)

    # Draws a dotted line to the end effector.
    glColor3f(1.0, 0.5, 0.5)
    draw_line([0, 0, 0], end_effector, dotted=True)

    # Draws the end effector dot.
    glColor3f(1.0, 0.5, 0.5)
    draw_dot(end_effector)

    # Draws the end effector axis.
    draw_axis(end_effector)


def camera() -> None:
    # Sets the matrix mode to the projection matrix, and loads the identity matrix.
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    # Generates the perspective matrix.
    gluPerspective(45, (WINDOW_WIDTH / WINDOW_HEIGHT), 0.1, 500.0)

    # Performs some camera transformations.
    glTranslatef(g_camera_position[0],
                 g_camera_position[1], g_camera_position[2])
    glRotatef(g_camera_rotation[0], 1.0, 0.0, 0.0)
    glRotatef(g_camera_rotation[1], 0.0, 1.0, 0.0)
    glRotatef(g_camera_rotation[2], 0.0, 0.0, 1.0)


def draw_line(start: any, end: any, width=10.0, dotted=False) -> None:
    if dotted:
        glEnable(GL_LINE_STIPPLE)
        glLineStipple(1, 0x0101)

    glLineWidth(width)
    glBegin(GL_LINES)
    glVertex3f(start[0], start[1], start[2])
    glVertex3f(end[0], end[1], end[2])
    glEnd()

    if dotted:
        glDisable(GL_LINE_STIPPLE)


def draw_axis(position: np.array = np.array([0, 0, 0]), size: float = 5.0) -> None:
    glColor4f(1.0, 0.0, 0.0, 0.7)
    draw_line(position, np.add(position, [size, 0.0, 0.0]), 4)
    glColor4f(0.0, 1.0, 0.0, 0.7)
    draw_line(position, np.add(position, [0.0, size, 0.0]), 4)
    glColor4f(0.0, 0.0, 1.0, 0.7)
    draw_line(position, np.add(position, [0.0, 0.0, size]), 4)


def render():
    # Clears the screen.
    glClearColor(0.4, 0.4, 0.4, 0.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    camera()
    draw_chain(bone_bottom, bone_top)
    draw_axis(size=10)

    glColor3f(0.2, 1.0, 0.2)
    draw_dot(g_ik_target, 10)

    if g_vis_mode == VisualizerMode.CIRCULAR:
        glColor3f(1.0, 1.0, 1.0)
        draw_circle(np.array([0, 16, 0]), rotation.along_axis(
            (1.0, 0.0, 0.0), rad(90)), g_circle_radius, width=2.0)


if not glfw.init():
    exit(0)

# Sets the OpenGL version.
window = glfw.create_window(
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, None, None)
if not window:
    glfw.terminate()
    exit(0)

glfw.set_key_callback(window, keypress)
glfw.set_window_attrib(window, glfw.RESIZABLE, False)
glfw.make_context_current(window)

glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

print(f'OpenGL Version: {glGetString(GL_VERSION)}')

while not glfw.window_should_close(window):
    # Performs the automatic IK modes.
    if g_vis_mode == VisualizerMode.RANDOM:
        if time.time() - g_last_random_ik_target > g_solve_interval:
            generate_random_ik_target()
            bone_bottom.reset_chain()
            ik(bone_bottom, bone_top, g_ik_target)
            phy.write_chain(bone_bottom)

            g_last_random_ik_target = time.time()
    elif g_vis_mode == VisualizerMode.CIRCULAR:
        if time.time() - g_last_random_ik_target > 0.02:
            g_ik_target = np.array([math.cos(
                time.time() / 20) * g_circle_radius, 16, math.sin(time.time() / 20) * g_circle_radius])
            ik(bone_bottom, bone_top, g_ik_target)
            g_last_random_ik_target = time.time()
            phy.write_chain(bone_bottom)

    # Polls the events.
    glfw.poll_events()

    # Performs the camera movements.
    if g_key_left_arrow_hold:
        g_camera_rotation[1] += 0.8
    if g_key_right_arrow_hold:
        g_camera_rotation[1] -= 0.8
    if g_key_top_arrow_hold:
        g_camera_rotation[0] += 0.8
    if g_key_bottom_arrow_hold:
        g_camera_rotation[0] -= 0.8

    if not g_key_right_shift_hold:
        if g_key_d_hold:
            g_camera_position[0] -= 0.8
        if g_key_a_hold:
            g_camera_position[0] += 0.8
        if g_key_w_hold:
            g_camera_position[2] += 0.8
        if g_key_s_hold:
            g_camera_position[2] -= 0.8
        if g_key_space_hold:
            g_camera_position[1] -= 0.8
        if g_key_shift_hold:
            g_camera_position[1] += 0.8
    if g_key_right_shift_hold and g_vis_mode == VisualizerMode.USER:
        modified: bool = False
        if g_key_d_hold:
            g_ik_target = np.add(g_ik_target, np.array([0.4, 0, 0]))
            modified = True
        if g_key_a_hold:
            g_ik_target = np.add(g_ik_target, np.array([-0.4, 0, 0]))
            modified = True
        if g_key_w_hold:
            g_ik_target = np.add(g_ik_target, np.array([0, 0, -0.4]))
            modified = True
        if g_key_s_hold:
            g_ik_target = np.add(g_ik_target, np.array([0, 0, 0.4]))
            modified = True
        if g_key_space_hold:
            g_ik_target = np.add(g_ik_target, np.array([0, 0.4, 0]))
            modified = True
        if g_key_shift_hold:
            g_ik_target = np.add(g_ik_target, np.array([0, -0.4, 0]))
            modified = True
        if modified:
            error: float = ik(bone_bottom, bone_top, g_ik_target)
            phy.write_chain(bone_bottom)

    # Calls the renderer.
    render()
    glfw.swap_buffers(window)

glfw.terminate()
