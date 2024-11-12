import trimesh
import numpy as np
from OpenGL.GL import *
from PIL import Image
from typing import Literal, List, Callable

from structs import Model


class SceneRemoveGraphNodes:
    """remove nodes from trimesh scene graph,
    can for instance be used to remove unwanted objects from scene
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
        flip (bool, optional): flip image vertically for opengl. Defaults to True.

    Returns:
        opengl_image (np array): image as np array formatted for opengl
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
        m (np array): model matrix

    Returns:
        model (Model): model struct
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

    return Model(
        vertices=vertices,
        faces=faces,
        normals=normals,
        colors=None,
        texture_coords=texture_coords,
        bounding_box=bounding_box,
        m=m,
    )


def load_model(
    path: str,
    m: np.ndarray,
    texture: Literal["none", "base_color", "uniform"] = "none",
    scene_transforms: List[Callable[[trimesh.Scene], trimesh.Scene]] = None,
    mesh_transforms: List[Callable[[trimesh.Trimesh], trimesh.Trimesh]] = None,
    uniform_color: List[float] = None,
):
    """load models from a file

    Args:
        path (str): path to model file
        m (np.ndarray): model matrix
        texture (Literal[&quot;none&quot;, &quot;base_color&quot;, &quot;uniform&quot;], optional): the texture mode to use. Defaults to "none".
        scene_transforms (List[Callable[[trimesh.Scene], trimesh.Scene]], optional): a list of transforms on a trimesh scene. Defaults to None.
        mesh_transforms (List[Callable[[trimesh.Trimesh], trimesh.Trimesh]], optional): a list of transforms on a trimesh mesh. Defaults to None.
        uniform_color (List[float], optional): the vertex color if texture mode is uniform. Defaults to None.

    Returns:
        Tuple[Model, PIL.Image]: (model struct, texture image)
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

    if texture == "none":
        texture_img = None
    if texture == "base_color":
        texture_img = pillow_to_opengl_rgba(mesh.visual.material.baseColorTexture)
    if texture == "uniform":
        texture_img = None
        assert uniform_color is not None
        assert len(uniform_color) == 3
        model.colors = np.repeat(
            np.array([*uniform_color, 1.0], dtype=np.float32)[None, :],
            model.vertices.shape[0],
            axis=0,
        )
    return model, texture_img
