from pathlib import Path
from PIL import Image
import numpy as np
from OpenGL.GL import *
import copy

from dataload import load_model, SceneRemoveGraphNodes, Model, pillow_to_opengl_rgba
from alloc import create_vao, create_2d_texture, create_cubemap_texture
from structs import RenderObject, Uniform
from geometry import (
    pose,
    translation,
    rotation_y,
)
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


def light_uniforms(m: np.ndarray):
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
    specular_strength = Uniform(
        name="specular_light_strength", value=SPECULAR_STRENGTH, type="float"
    )
    specular_shininess = Uniform(
        name="specular_light_shininess", value=SPECULAR_SHININESS, type="float"
    )
    # camera position, model matrix, normal matrix uniforms are computed and set in render loop
    return [
        ambient_strength,
        ambient_color,
        diffuse_pos,
        diffuse_color,
        specular_strength,
        specular_shininess,
    ]


def rotation_animation(model: Model):
    model.m = rotation_y(0.1) @ model.m
    return model


def olympic_rings(shaders: int):
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
    )
    reflection_strength = Uniform(name="reflection_strength", value=0.0, type="float")
    return RenderObject(
        model=model,
        vao=vao,
        vbos=vbos,
        shaders=shaders,
        textures=[texture],
        static_uniforms=[
            texture_sampler,
            reflection_strength,
            *light_uniforms(model.m),
        ],
        animation_function=None,
    )


def floor(shaders: int):
    """create a 5x5 grid of floor tiles centered at the origin,
    each tile is 2x2, so the grid is 10x10

    Returns:
        List[RenderObject]: floor tiles
    """
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
    reflection_strength = Uniform(name="reflection_strength", value=0.0, type="float")
    return [
        RenderObject(
            model=m,
            vao=vao,
            vbos=vbos,
            shaders=shaders,
            textures=[texture],
            static_uniforms=[
                texture_sampler_uniform,
                reflection_strength,
                *light_uniforms(m.m),
            ],
            animation_function=None,
        )
        for m in model_copies
    ]


def sky_box(shaders: int):
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
        {"nx": nx, "px": px, "ny": ny, "py": py, "nz": nz, "pz": pz}, GL_TEXTURE1
    )
    vao, vbos = create_vao(model, shaders)
    texture_sampler_uniform = Uniform(
        name="skybox_sampler", value=texture.unit - GL_TEXTURE0, type="int"
    )
    return RenderObject(
        model=model,
        vao=vao,
        vbos=vbos,
        shaders=shaders,
        textures=[texture],
        static_uniforms=[texture_sampler_uniform],
        animation_function=None,
    )


def olympic_logo(shaders: int, skybox: RenderObject):
    assert (
        skybox.textures is not None and len(skybox.textures) == 1
    ), "skybox does not have exactly one texture"
    assert (
        skybox.static_uniforms is not None and len(skybox.static_uniforms) == 1
    ), "skybox does not have exactly one static uniform (sampler)"
    assert skybox.textures[0].unit == GL_TEXTURE1, "skybox texture unit is not 1"

    model, _ = load_model(
        "models/olympics_paris/scene.gltf",
        m=pose(),
        texture=None,
    )
    height = model.bounding_box[1, 1] - model.bounding_box[0, 1]
    model.m = translation([0.0, 0.5 * height, 0.0]) @ model.m
    vao, vbos = create_vao(model, shaders)
    reflection_strength = Uniform(name="reflection_strength", value=1.0, type="float")
    return RenderObject(
        model=model,
        vao=vao,
        vbos=vbos,
        shaders=shaders,
        textures=skybox.textures,
        static_uniforms=[
            reflection_strength,
            *light_uniforms(model.m),
            *skybox.static_uniforms,
        ],
        animation_function=rotation_animation,
    )
