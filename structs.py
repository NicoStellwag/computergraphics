from dataclasses import dataclass
import numpy as np
from typing import Literal, List


@dataclass
class Camera:
    center: np.ndarray
    psi: float
    phi: float
    distance: float


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
    vbos: List[int]
    shaders: int
    texture: int
    texture_type: int
    texture_unit: int
    static_uniforms: List[Uniform]
