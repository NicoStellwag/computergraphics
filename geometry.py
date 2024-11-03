from dataclasses import dataclass
import numpy as np


WINDOW_SIZE = (800, 600)


@dataclass
class Camera:
    center: np.ndarray = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    psi: float = 0.0  # vertical
    phi: float = 0.0  # horizontal
    distance: float = 5.0

    def V(self):
        D = translation(-self.center)
        R = rotation_x(self.psi) @ rotation_y(self.phi)
        T = translation([0.0, 0.0, -self.distance])
        return T @ R @ D

    def V_no_translation(self):
        R = rotation_x(self.psi) @ rotation_y(self.phi)
        return R


def rotation_x(angle):
    m = np.eye(4)
    m[1, 1] = np.cos(angle)
    m[1, 2] = -np.sin(angle)
    m[2, 1] = np.sin(angle)
    m[2, 2] = np.cos(angle)
    return m


def rotation_y(angle):
    m = np.eye(4)
    m[0, 0] = np.cos(angle)
    m[0, 2] = np.sin(angle)
    m[2, 0] = -np.sin(angle)
    m[2, 2] = np.cos(angle)
    return m


def rotation_z(angle):
    m = np.eye(4)
    m[0, 0] = np.cos(angle)
    m[0, 1] = -np.sin(angle)
    m[1, 0] = np.sin(angle)
    m[1, 1] = np.cos(angle)
    return m


def translation(position):
    m = np.eye(4)
    m[0, 3] = position[0]
    m[1, 3] = position[1]
    m[2, 3] = position[2]
    return m


def frustum(left, right, bottom, top, near, far):
    m = np.zeros((4, 4))
    m[0, 0] = 2 * near / (right - left)
    m[1, 1] = 2 * near / (top - bottom)
    m[0, 2] = (right + left) / (right - left)
    m[1, 2] = (top + bottom) / (top - bottom)
    m[2, 2] = -(far + near) / (far - near)
    m[3, 2] = -1
    m[2, 3] = -2 * far * near / (far - near)
    return m


def pose(position=[0.0, 0.0, 0.0], orientation=0.0, scale=[1.0, 1.0, 1.0]):
    T = translation(position)
    R = rotation_y(orientation)
    S = np.eye(4)
    if isinstance(scale, (int, float)):
        scale = [scale] * 3
    S[0, 0] = scale[0]
    S[1, 1] = scale[1]
    S[2, 2] = scale[2]
    return T @ R @ S


def P():
    fovy = np.radians(60)
    aspect = WINDOW_SIZE[0] / WINDOW_SIZE[1]
    near = 0.1
    far = 20.0
    top = near * np.tan(fovy / 2)
    right = top * aspect
    return frustum(-right, right, -top, top, near, far)


def np_to_opengl(m):
    return np.ascontiguousarray(m.T)
