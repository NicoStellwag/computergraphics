from pathlib import Path
from PIL import Image
import numpy as np
from OpenGL.GL import *
import copy

from shaders import compile_shaders
from dataload import load_model, SceneRemoveGraphNodes, Model, pillow_to_opengl_rgba
from alloc import create_vao, create_2d_texture, create_cubemap_texture
from structs import RenderObject, Uniform
from geometry import pose, translation


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
        m=pose(),
        texture="base_color",
        scene_transforms=[SceneRemoveGraphNodes(["Object_23", "Grass"])],
    )
    height = model.bounding_box[1, 1] - model.bounding_box[0, 1]
    model.m = translation([0.0, 0.5 * height, -4.0]) @ model.m
    texture = create_2d_texture(texture_img)
    vao = create_vao(model, shaders)
    texture_sampler_uniform = Uniform(
        name="texture_sampler", value=0, type="int"
    )  # always use texture unit 0 for now
    return RenderObject(
        model=model,
        vao=vao,
        shaders=shaders,
        texture=texture,
        texture_type=GL_TEXTURE_2D,
        texture_unit=GL_TEXTURE0,
        uniforms=[texture_sampler_uniform],
    )


def bunny_world():
    shaders = compile_shaders("plain_model")
    model, _ = load_model(
        "models/bunny_world.obj",
        m=pose(scale=0.5, position=[1.5, 0.0, 0.0], orientation=180),
        texture=None,
    )
    vao = create_vao(model, shaders)
    return RenderObject(
        model=model,
        vao=vao,
        shaders=shaders,
        texture=None,
        texture_type=None,
        texture_unit=None,
        uniforms=None,
    )


def floor():
    """create a 5x5 grid of floor tiles centered at the origin,
    each tile is 2x2, so the grid is 10x10

    Returns:
        List[RenderObject]: floor tiles
    """
    shaders = compile_shaders("textured_model")
    model, texture_img = load_model(
        "models/floor_material.glb",
        m=pose(position=[0.0, 0.0, 0.0]),
        texture="base_color",
    )

    size_x = model.bounding_box[0, 0] - model.bounding_box[1, 0]
    size_z = model.bounding_box[0, 2] - model.bounding_box[1, 2]
    model_copies = []
    for x in range(5):
        for z in range(5):
            c = copy.deepcopy(model)
            c.m = pose(position=[x * size_x, 0.0, z * size_z])
            model_copies.append(c)

    for c in model_copies:
        c.m = translation([-2 * size_x, 0.0, -2 * size_z]) @ c.m

    texture = create_2d_texture(texture_img)
    vao = create_vao(model, shaders)
    texture_sampler_uniform = Uniform(name="texture_sampler", value=0, type="int")
    return [
        RenderObject(
            model=m,
            vao=vao,
            shaders=shaders,
            texture=texture,
            texture_type=GL_TEXTURE_2D,
            texture_unit=GL_TEXTURE0,
            uniforms=[texture_sampler_uniform],
        )
        for m in model_copies
    ]


def sky_box():
    shaders = compile_shaders("cubemap")
    model = Model(
        vertices=CUBEMAP_VERTICES,
        faces=None,
        normals=None,
        texture_coords=None,
        bounding_box=None,
        m=pose(),
    )
    # base_dir = Path("textures/paris_cubemap")
    # px = pillow_to_opengl_rgba(Image.open(base_dir / "px.png"), omit_flip=True)
    # nx = pillow_to_opengl_rgba(Image.open(base_dir / "nx.png"), omit_flip=True)
    # py = pillow_to_opengl_rgba(Image.open(base_dir / "py.png"), omit_flip=True)
    # ny = pillow_to_opengl_rgba(Image.open(base_dir / "ny.png"), omit_flip=True)
    # pz = pillow_to_opengl_rgba(Image.open(base_dir / "pz.png"), omit_flip=True)
    # nz = pillow_to_opengl_rgba(Image.open(base_dir / "nz.png"), omit_flip=True)
    base_dir = Path("textures/night_stars_skybox")
    px = pillow_to_opengl_rgba(Image.open(base_dir / "right.png"), omit_flip=True)
    nx = pillow_to_opengl_rgba(Image.open(base_dir / "left.png"), omit_flip=True)
    py = pillow_to_opengl_rgba(Image.open(base_dir / "top.png"), omit_flip=True)
    ny = pillow_to_opengl_rgba(Image.open(base_dir / "bottom.png"), omit_flip=True)
    pz = pillow_to_opengl_rgba(Image.open(base_dir / "front.png"), omit_flip=True)
    nz = pillow_to_opengl_rgba(Image.open(base_dir / "back.png"), omit_flip=True)
    texture = create_cubemap_texture(
        {"nx": nx, "px": px, "ny": ny, "py": py, "nz": nz, "pz": pz}
    )
    vao = create_vao(model, shaders)
    texture_sampler_uniform = Uniform(name="texture_sampler", value=0, type="int")
    return RenderObject(
        model=model,
        vao=vao,
        shaders=shaders,
        texture=texture,
        texture_type=GL_TEXTURE_CUBE_MAP,
        texture_unit=GL_TEXTURE0,
        uniforms=[texture_sampler_uniform],
    )
