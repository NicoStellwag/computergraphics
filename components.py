from pathlib import Path
from PIL import Image
import numpy as np
from OpenGL.GL import *

from shaders import compile_shaders
from dataload import load_model, SceneRemoveGraphNodes, Model, pillow_to_opengl_rgba
from alloc import create_vao, create_2d_texture, create_cubemap_texture
from render import RenderObject
from geometry import pose


CUBEMAP_VERTICES = np.array(
    [
        [-1.0, 1.0, -1.0],
        [-1.0, -1.0, -1.0],
        [1.0, -1.0, -1.0],
        [1.0, -1.0, -1.0],
        [1.0, 1.0, -1.0],
        [-1.0, 1.0, -1.0],
        [-1.0, -1.0, 1.0],
        [-1.0, -1.0, -1.0],
        [-1.0, 1.0, -1.0],
        [-1.0, 1.0, -1.0],
        [-1.0, 1.0, 1.0],
        [-1.0, -1.0, 1.0],
        [1.0, -1.0, -1.0],
        [1.0, -1.0, 1.0],
        [1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0],
        [1.0, 1.0, -1.0],
        [1.0, -1.0, -1.0],
        [-1.0, -1.0, 1.0],
        [-1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0],
        [1.0, -1.0, 1.0],
        [-1.0, -1.0, 1.0],
        [-1.0, 1.0, -1.0],
        [1.0, 1.0, -1.0],
        [1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0],
        [-1.0, 1.0, 1.0],
        [-1.0, 1.0, -1.0],
        [-1.0, -1.0, -1.0],
        [-1.0, -1.0, 1.0],
        [1.0, -1.0, -1.0],
        [1.0, -1.0, -1.0],
        [-1.0, -1.0, 1.0],
        [1.0, -1.0, 1.0],
    ],
    dtype=np.float32,
)


def olympic_rings():
    shaders = compile_shaders("textured_model")
    model, texture_img = load_model(
        "models/olympic_rings.glb",
        M=pose(position=[-1.5, 0.0, 0.0]),
        texture="base_color",
        scene_transforms=[SceneRemoveGraphNodes(["Object_23", "Grass"])],
    )
    texture = create_2d_texture(texture_img)
    vao = create_vao(model, shaders)
    return RenderObject(
        model=model,
        vao=vao,
        shaders=shaders,
        texture=texture,
        texture_type=GL_TEXTURE_2D,
    )


def bunny_world():
    shaders = compile_shaders("plain_model")
    model, _ = load_model(
        "models/bunny_world.obj",
        M=pose(scale=0.5, position=[1.5, 0.0, 0.0], orientation=180),
        texture=None,
    )
    vao = create_vao(model, shaders)
    return RenderObject(
        model=model, vao=vao, shaders=shaders, texture=None, texture_type=None
    )


def sky_box():
    shaders = compile_shaders("cubemap")
    model = Model(
        vertices=CUBEMAP_VERTICES,
        faces=None,
        normals=None,
        texture_coords=None,
        M=pose(),
    )
    base_dir = Path("textures/paris_cubemap")
    nx = pillow_to_opengl_rgba(Image.open(base_dir / "nx.png"), omit_flip=True)
    px = pillow_to_opengl_rgba(Image.open(base_dir / "px.png"), omit_flip=True)
    ny = pillow_to_opengl_rgba(Image.open(base_dir / "ny.png"), omit_flip=True)
    py = pillow_to_opengl_rgba(Image.open(base_dir / "py.png"), omit_flip=True)
    nz = pillow_to_opengl_rgba(Image.open(base_dir / "nz.png"), omit_flip=True)
    pz = pillow_to_opengl_rgba(Image.open(base_dir / "pz.png"), omit_flip=True)
    texture = create_cubemap_texture(
        {"nx": nx, "px": px, "ny": ny, "py": py, "nz": nz, "pz": pz}
    )
    vao = create_vao(model, shaders)
    return RenderObject(
        model=model,
        vao=vao,
        shaders=shaders,
        texture=texture,
        texture_type=GL_TEXTURE_CUBE_MAP,
    )
