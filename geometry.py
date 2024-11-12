import numpy as np
from typing import List, Tuple

from structs import Camera


def V(camera: Camera):
    """retrieve view matrix from camera struct

    Args:
        camera (Camera): camera struct

    Returns:
        np array: view matrix
    """
    D = translation(-camera.center)
    R = rotation_x(camera.psi) @ rotation_y(camera.phi)
    T = translation([0.0, 0.0, -camera.distance])
    return T @ R @ D


def V_no_translation(camera: Camera):
    """retrieve view matrix from camera struct without translation

    Args:
        camera (Camera): camera struct

    Returns:
        np array: view matrix without translation component
    """
    R = rotation_x(camera.psi) @ rotation_y(camera.phi)
    return R


def rotation_x(angle: float):
    """create a rotation matrix around x axis

    Args:
        angle (float): angle in radians

    Returns:
        np array: rotation matrix
    """
    m = np.eye(4)
    m[1, 1] = np.cos(angle)
    m[1, 2] = -np.sin(angle)
    m[2, 1] = np.sin(angle)
    m[2, 2] = np.cos(angle)
    return m


def rotation_y(angle: float):
    """create a rotation matrix around y axis

    Args:
        angle (float): angle in radians

    Returns:
        np array: rotation matrix
    """
    m = np.eye(4)
    m[0, 0] = np.cos(angle)
    m[0, 2] = np.sin(angle)
    m[2, 0] = -np.sin(angle)
    m[2, 2] = np.cos(angle)
    return m


def rotation_z(angle: float):
    """create a rotation matrix around z axis

    Args:
        angle (float): angle in radians

    Returns:
        np array: rotation matrix
    """
    m = np.eye(4)
    m[0, 0] = np.cos(angle)
    m[0, 1] = -np.sin(angle)
    m[1, 0] = np.sin(angle)
    m[1, 1] = np.cos(angle)
    return m


def translation(position: List[float]):
    """create a translation matrix

    Args:
        position (List[float]): position in x, y, z fomat

    Returns:
        np array: translation matrix
    """
    m = np.eye(4)
    m[0, 3] = position[0]
    m[1, 3] = position[1]
    m[2, 3] = position[2]
    return m


def frustum(
    left: float, right: float, bottom: float, top: float, near: float, far: float
):
    """create a frustum matrix for perspective projection

    Args:
        left (float): left parameter
        right (float): right parameter
        bottom (float): bottom parameter
        top (float): top parameter
        near (float): near parameter
        far (float): far parameter

    Returns:
        np array: frustum matrix
    """
    m = np.zeros((4, 4))
    m[0, 0] = 2 * near / (right - left)
    m[1, 1] = 2 * near / (top - bottom)
    m[0, 2] = (right + left) / (right - left)
    m[1, 2] = (top + bottom) / (top - bottom)
    m[2, 2] = -(far + near) / (far - near)
    m[3, 2] = -1
    m[2, 3] = -2 * far * near / (far - near)
    return m


def pose(
    position: List[float] = [0.0, 0.0, 0.0],
    orientation: float = 0.0,
    scale: List[float] | float = [1.0, 1.0, 1.0],
):
    """construct a pose matrix

    Args:
        position (List[float], optional): position of the object in x, y, z. Defaults to [0.0, 0.0, 0.0].
        orientation (float, optional): angle around y axis in radians. Defaults to 0.0.
        scale (List[float] | float, optional): scale values for x, y, z or uniform scaling if scalar. Defaults to [1.0, 1.0, 1.0].

    Returns:
        np array: pose matrix
    """
    T = translation(position)
    R = rotation_y(orientation)
    S = np.eye(4)
    if isinstance(scale, (int, float)):
        scale = [scale] * 3
    S[0, 0] = scale[0]
    S[1, 1] = scale[1]
    S[2, 2] = scale[2]
    return T @ R @ S


def normal_from_model_matrix(m: np.ndarray):
    """compute a normal matrix from a model matrix,
    the normal matrix transforms vertice normals from local object space to world space

    Args:
        m (np array): 4x4 model matrix

    Returns:
        np array: 3x3 normal matrix
    """
    return np.linalg.inv(m[:3, :3]).T


def camera_position(camera: Camera):
    """get camera position from camera struct

    Args:
        camera (Camera): camera struct

    Returns:
        np array: camera position
    """
    return np.linalg.inv(V(camera))[:3, 3]


def P(window_size: Tuple[int, int]):
    """create a projection matrix for perspective projection

    Args:
        window_size (Tuple[int, int]): pygame window size [width, height]

    Returns:
        np array: projection matrix (frustum)
    """
    fovy = np.radians(60)
    aspect = window_size[0] / window_size[1]
    near = 0.1
    far = 20.0
    top = near * np.tan(fovy / 2)
    right = top * aspect
    return frustum(-right, right, -top, top, near, far)


def np_matrix_to_opengl(m: np.ndarray):
    """format a np matrix for opengl (column major, and contiguous)

    Args:
        m (np array): matrix

    Returns:
        np array: matrix formatted for opengl
    """
    return np.ascontiguousarray(m.T)
