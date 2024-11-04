from dataclasses import dataclass
import numpy as np


@dataclass
class Camera:
    center: np.ndarray = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    psi: float = 0.0  # vertical
    phi: float = 0.0  # horizontal
    distance: float = 5.0


@dataclass
class Model:
    vertices: np.ndarray
    faces: np.ndarray
    normals: np.ndarray
    texture_coords: np.ndarray
    bounding_box: np.ndarray  # 2 x 3
    m: np.ndarray


@dataclass
class RenderObject:
    model: Model
    vao: int
    shaders: int
    texture: int
    texture_type: int
