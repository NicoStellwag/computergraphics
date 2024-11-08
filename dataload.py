import trimesh
import numpy as np
from OpenGL.GL import *
from PIL import Image

from structs import Model


class SceneRemoveGraphNodes:
    """remove nodes from trimesh scene graph,
    can e.g. be used to remove unwanted objects from scene
    """

    def __init__(self, graph_nodes):
        self.graph_nodes = graph_nodes

    def __call__(self, scene):
        for node in self.graph_nodes:
            scene.graph.transforms.remove_node(node)
        return scene


def pillow_to_opengl_rgba(pillow_img, flip=True):
    """convert pillow image to np array for opengl

    Args:
        pillow_img (PIL.Image): pillow image

    Returns:
        np array: opengl image
    """
    if flip:
        opengl_img = pillow_img.transpose(Image.FLIP_TOP_BOTTOM)
    else:
        opengl_img = pillow_img
    opengl_img = np.asarray(opengl_img.convert("RGBA"), dtype=np.uint8)
    return opengl_img


def mesh_to_model(mesh, m):
    """generate model struct from trimesh mesh

    Args:
        mesh (trimesh.Mesh): mesh
        M (np array): model matrix

    Returns:
        Model: model struct
    """
    vertices = np.ascontiguousarray(mesh.vertices).astype(np.float32)
    faces = np.ascontiguousarray(mesh.faces).astype(np.uint32)
    normals = np.ascontiguousarray(mesh.vertex_normals).astype(np.float32)

    # center vertices at origin and scale to [-1, 1]
    ma = vertices.max(axis=0)
    mi = vertices.min(axis=0)
    center = (ma + mi) / 2
    vertices -= center
    scale = np.abs(vertices).max()
    vertices /= scale

    bounding_box = np.stack([vertices.min(0), vertices.max(0)], axis=0)

    # texture coordinates if present
    if hasattr(mesh.visual, "uv"):
        texture_coords = np.ascontiguousarray(mesh.visual.uv).astype(np.float32)
    else:
        texture_coords = None

    # sanity checks
    assert vertices.shape[0] == normals.shape[0]
    if texture_coords is not None:
        assert vertices.shape[0] == texture_coords.shape[0]

    return Model(vertices, faces, normals, texture_coords, bounding_box, m)


def load_model(path, m, texture=None, scene_transforms=None, mesh_transforms=None):
    """create a model struct from file

    Args:
        path (str): path to model file
        M (np array): model matrix
        scene_transforms (List[function], optional): list of functions that modify trimesh scene. Defaults to None.
        mesh_transforms (List[function], optional): list of functions that modify trimesh mesh. Defaults to None.

    Returns:
        (Model, np array): tuple of model struct and texture image
    """
    mesh = trimesh.load_mesh(path)

    if isinstance(mesh, trimesh.Scene):
        if scene_transforms is not None:
            for transform in scene_transforms:
                mesh = transform(mesh)
        mesh = mesh.to_mesh()

    if mesh_transforms is not None:
        for transform in mesh_transforms:
            mesh = transform(mesh)

    model = mesh_to_model(mesh, m)

    if texture is None:
        texture_img = None
        model.texture_coords = None  # ! tmp
    if texture == "base_color":
        texture_img = pillow_to_opengl_rgba(mesh.visual.material.baseColorTexture)
    return model, texture_img
