from shaders import compile_shaders
from model import load_model, SceneRemoveGraphNodes
from matutils import poseMatrix
from alloc import create_vao, create_texture
from render import RenderObject


def olympic_rings():
    ring_shaders = compile_shaders("textured_model")
    ring_model, ring_texture_img = load_model(
        "models/olympic_rings.glb",
        M=poseMatrix(),
        texture="base_color",
        scene_transforms=[SceneRemoveGraphNodes(["Object_23", "Grass"])],
    )
    ring_texture = create_texture(ring_texture_img)
    ring_vao = create_vao(ring_model, ring_shaders)
    return RenderObject(ring_model, ring_vao, ring_shaders, ring_texture)


def bunny_world():
    bunny_world_shaders = compile_shaders("plain_model")
    bunny_world_model, _ = load_model(
        "models/bunny_world.obj",
        M=poseMatrix(scale=0.1, position=[0.0, 0.0, 2.0]),
        texture=None,
    )
    bunny_world_vao = create_vao(bunny_world_model, bunny_world_shaders)
    return RenderObject(bunny_world_model, bunny_world_vao, bunny_world_shaders, None)
