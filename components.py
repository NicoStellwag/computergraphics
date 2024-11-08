from pathlib import Path
from PIL import Image
import numpy as np
from OpenGL.GL import *
import copy

from shaders import compile_shaders
from dataload import load_model, SceneRemoveGraphNodes, Model, pillow_to_opengl_rgba
from alloc import create_vao, create_2d_texture, create_cubemap_texture
from structs import RenderObject, Uniform
from geometry import pose, translation, np_matrix_to_opengl, normal_from_model_matrix
from light import (
    AMBIENT_STRENGTH,
    AMBIENT_COLOR,
    DIFFUSE_POS,
    DIFFUSE_COLOR,
    SPECULAR_STRENGTH,
    SPECULAR_SHININESS,
)


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


def light_uniforms(m):
    ambient_strength = Uniform(
        name="ambient_light_strength", value=AMBIENT_STRENGTH, type="float"
    )
    ambient_color = Uniform(
        name="ambient_light_color", value=AMBIENT_COLOR, type="vec3"
    )
    diffuse_pos = Uniform(name="diffuse_light_position", value=DIFFUSE_POS, type="vec3")
    diffuse_color = Uniform(
        name="diffuse_light_color", value=DIFFUSE_COLOR, type="vec3"
    )
    model_matrix = Uniform(name="M", value=np_matrix_to_opengl(m), type="mat4")
    normal_matrix = Uniform(
        name="normal_matrix",
        value=np_matrix_to_opengl(normal_from_model_matrix(m)),
        type="mat3",
    )
    specular_strength = Uniform(
        name="specular_light_strength", value=SPECULAR_STRENGTH, type="float"
    )
    specular_shininess = Uniform(
        name="specular_light_shininess", value=SPECULAR_SHININESS, type="float"
    )
    # camera position uniform is computed and set in render loop
    return [
        ambient_strength,
        ambient_color,
        diffuse_pos,
        diffuse_color,
        specular_strength,
        specular_shininess,
        model_matrix,
        normal_matrix,
    ]


def olympic_rings():
    shaders = compile_shaders("object")
    model, texture_img = load_model(
        "models/olympic_rings.glb",
        m=pose(),
        texture="base_color",
        scene_transforms=[SceneRemoveGraphNodes(["Object_23", "Grass"])],
    )
    height = model.bounding_box[1, 1] - model.bounding_box[0, 1]
    model.m = translation([0.0, 0.5 * height, -4.0]) @ model.m
    texture = create_2d_texture(texture_img, GL_TEXTURE0)
    vao, vbos = create_vao(model, shaders)
    texture_sampler = Uniform(
        name="texture_sampler", value=texture.unit - GL_TEXTURE0, type="int"
    )  # always use texture unit 0 for now
    return RenderObject(
        model=model,
        vao=vao,
        vbos=vbos,
        shaders=shaders,
        textures=[texture],
        static_uniforms=[texture_sampler, *light_uniforms(model.m)],
    )


def floor():
    """create a 5x5 grid of floor tiles centered at the origin,
    each tile is 2x2, so the grid is 10x10

    Returns:
        List[RenderObject]: floor tiles
    """
    shaders = compile_shaders("object")
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

    texture = create_2d_texture(texture_img, GL_TEXTURE0)
    vao, vbos = create_vao(model, shaders)
    texture_sampler_uniform = Uniform(
        name="texture_sampler", value=texture.unit - GL_TEXTURE0, type="int"
    )
    return [
        RenderObject(
            model=m,
            vao=vao,
            vbos=vbos,
            shaders=shaders,
            textures=[texture],
            static_uniforms=[texture_sampler_uniform, *light_uniforms(m.m)],
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
    px = pillow_to_opengl_rgba(Image.open(base_dir / "right.png"), flip=False)
    nx = pillow_to_opengl_rgba(Image.open(base_dir / "left.png"), flip=False)
    py = pillow_to_opengl_rgba(Image.open(base_dir / "top.png"), flip=False)
    ny = pillow_to_opengl_rgba(Image.open(base_dir / "bottom.png"), flip=False)
    pz = pillow_to_opengl_rgba(Image.open(base_dir / "front.png"), flip=False)
    nz = pillow_to_opengl_rgba(Image.open(base_dir / "back.png"), flip=False)
    texture = create_cubemap_texture(
        {"nx": nx, "px": px, "ny": ny, "py": py, "nz": nz, "pz": pz}, GL_TEXTURE0
    )
    vao, vbos = create_vao(model, shaders)
    texture_sampler_uniform = Uniform(
        name="texture_sampler", value=texture.unit - GL_TEXTURE0, type="int"
    )
    return RenderObject(
        model=model,
        vao=vao,
        vbos=vbos,
        shaders=shaders,
        textures=[texture],
        static_uniforms=[texture_sampler_uniform],
    )
