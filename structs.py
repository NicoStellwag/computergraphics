from dataclasses import dataclass
import numpy as np
from typing import Literal, List, Callable


@dataclass
class Camera:
    center: np.ndarray
    psi: float  # x
    phi: float  # y
    distance: float


@dataclass
class Model:
    vertices: np.ndarray
    faces: np.ndarray
    normals: np.ndarray
    colors: np.ndarray
    texture_coords: np.ndarray
    bounding_box: np.ndarray  # 2 x 3
    m: np.ndarray


@dataclass
class Uniform:
    name: str  # must match shader program
    value: object
    type: Literal["int", "float", "vec3", "mat3", "mat4"]


@dataclass
class Texture:
    id: int
    type: int
    unit: int


@dataclass
class RenderObject:
    model: Model
    textures: List[Texture]
    vao: int
    vbos: List[int]
    shaders: int
    static_uniforms: List[Uniform]
    animation_function: Callable[[Model], Model]
