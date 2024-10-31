from dataclasses import dataclass
import trimesh
import numpy as np
from OpenGL.GL import *
from PIL import Image


@dataclass
class Model:
    vertices: np.ndarray
    faces: np.ndarray
    normals: np.ndarray
    texture_coords: np.ndarray
    M: np.ndarray


def load_model(path, M):
    """create a model struct from file

    Args:
        path (str): path to model file

    Returns:
        (Model, np array): tuple of model struct and texture image
    """
    mesh = trimesh.load_mesh(path)
    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(mesh.dump())
    vertices = mesh.vertices.astype(np.float32)
    faces = mesh.faces.astype(np.uint32)
    normals = mesh.vertex_normals.astype(np.float32)
    texture_coords = mesh.visual.uv.astype(np.float32)
    assert vertices.shape[0] == normals.shape[0] == texture_coords.shape[0]
    model = Model(vertices, faces, normals, texture_coords, M)

    texture_img = mesh.visual.material.baseColorTexture
    texture_img = texture_img.transpose(Image.FLIP_TOP_BOTTOM)
    texture_img = np.asarray(texture_img.convert("RGBA"), dtype=np.uint8)
    return model, texture_img
