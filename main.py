import os

os.environ["SDL_VIDEO_X11_FORCE_EGL"] = "1"  # hack for linux vm on mac

import pygame
from OpenGL.GL import *
import numpy as np
from typing import Tuple

from structs import Camera
from components import olympic_rings, sky_box, floor, olympic_logo, human_body
from render import render_loop
from geometry import P
from alloc import destroy_render_object
from shaders import compile_shaders

WINDOW_SIZE = (800, 600)


def init_pygame(window_size: Tuple[int, int]):
    """initialize pygame window

    Args:
        window_size (Tuple[int, int]): window size (width, height)
    """
    pygame.init()
    pygame.display.set_mode(window_size, pygame.DOUBLEBUF | pygame.OPENGL, 24)
    pygame.display.set_caption("Olympics Paris 2024")


def init_opengl(window_size: Tuple[int, int]):
    """initialize opengl context

    Args:
        window_size (Tuple[int, int]): window size (width, height)
    """
    glViewport(0, 0, window_size[0], window_size[1])
    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    # glEnableClientState(GL_VERTEX_ARRAY) # deprecated
    # glClearColor(0.7, 0.7, 1.0, 1.0) # sky box anyway


def main():
    init_pygame(WINDOW_SIZE)
    init_opengl(WINDOW_SIZE)

    p = P(WINDOW_SIZE)

    camera = Camera(
        center=np.array([0.0, 1.0, 0.0], dtype=np.float32),
        psi=0.0,
        phi=0.0,
        distance=3.0,
    )

    object_shaders = compile_shaders("object")
    skybox_shaders = compile_shaders("cubemap")

    skybox = sky_box(skybox_shaders)
    objects = []
    objects += floor(object_shaders)
    objects.append(olympic_rings(object_shaders))
    objects.append(olympic_logo(object_shaders, skybox))
    objects.append(human_body(object_shaders))

    render_loop(
        window_size=WINDOW_SIZE,
        camera=camera,
        p=p,
        objects=objects,
        skybox=skybox,
    )

    for ro in objects + [skybox]:
        destroy_render_object(ro)


if __name__ == "__main__":
    main()
