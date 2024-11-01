import os

os.environ["SDL_VIDEO_X11_FORCE_EGL"] = "1"  # hack for linux vm on mac

import pygame
from OpenGL.GL import *

from events import handle_events
from geometry import WINDOW_SIZE, P, Camera
from model import load_model, SceneRemoveGraphNodes
from alloc import create_vao, create_texture
from shaders import compile_shaders
from matutils import poseMatrix
from render import RenderObject, draw


def init_pygame(window_size):
    pygame.init()
    pygame.display.set_mode(window_size, pygame.DOUBLEBUF | pygame.OPENGL, 24)
    pygame.display.set_caption("Olympics Paris 2024")


def init_opengl(window_size):
    glViewport(0, 0, window_size[0], window_size[1])
    glClearColor(0.7, 0.7, 1.0, 1.0)
    glEnable(GL_CULL_FACE)
    # glEnableClientState(GL_VERTEX_ARRAY)
    glEnable(GL_DEPTH_TEST)


def render_loop(camera, render_objects):
    running = True
    mouse_mvt = None
    clock = pygame.time.Clock()
    while running:
        running, camera, mouse_mvt = handle_events(
            camera=camera, window_size=WINDOW_SIZE, prev_mouse_mvt=mouse_mvt
        )
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for render_object in render_objects:
            draw(render_object, camera, P)
        pygame.display.flip()
        clock.tick(60)


def main():
    init_pygame(WINDOW_SIZE)
    init_opengl(WINDOW_SIZE)
    camera = Camera()

    # rings
    ring_shaders = compile_shaders("textured_model")
    ring_model, ring_texture_img = load_model(
        "models/olympic_rings.glb",
        M=poseMatrix(),
        texture="base_color",
        scene_transforms=[SceneRemoveGraphNodes(["Object_23", "Grass"])],
    )
    ring_texture = create_texture(ring_texture_img)
    ring_vao = create_vao(ring_model, ring_shaders)
    rings = RenderObject(ring_model, ring_vao, ring_shaders, ring_texture)

    # # bunny_world
    # bunny_world_shaders = compile_shaders("plain_model")
    # bunny_world_model, _ = load_model(
    #     "../sheets/5/models/bunny_world.obj",
    #     M=poseMatrix(),
    #     texture=None,
    # )
    # bunny_world_vao = create_vao(bunny_world_model, bunny_world_shaders)
    # bunny_world = RenderObject(
    #     bunny_world_model, bunny_world_vao, bunny_world_shaders, None
    # )

    render_loop(camera, [rings])


if __name__ == "__main__":
    main()
