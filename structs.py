from dataclasses import dataclass
import numpy as np
from typing import Literal, List


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
class Uniform:
    name: str  # must match shader program
    value: object
    type: Literal["int", "float", "vec3", "mat3", "mat4"]


@dataclass
class RenderObject:
    model: Model
    vao: int
    shaders: int
    texture: int
    texture_type: int
    texture_unit: int
    uniforms: List[
        Uniform
    ]  # all uniforms except pvm, which is has to be calculated in the render loop
