import os

os.environ["SDL_VIDEO_X11_FORCE_EGL"] = "1"  # hack for linux vm on mac

import pygame
from OpenGL.GL import *

from geometry import WINDOW_SIZE, P, Camera
from components import olympic_rings, bunny_world
from render import render_loop


def init_pygame(window_size):
    pygame.init()
    pygame.display.set_mode(window_size, pygame.DOUBLEBUF | pygame.OPENGL, 24)
    pygame.display.set_caption("Olympics Paris 2024")


def init_opengl(window_size):
    glViewport(0, 0, window_size[0], window_size[1])
    glClearColor(0.7, 0.7, 1.0, 1.0)
    glEnable(GL_CULL_FACE)
    # glEnableClientState(GL_VERTEX_ARRAY) # deprecated
    glEnable(GL_DEPTH_TEST)


def main():
    init_pygame(WINDOW_SIZE)
    init_opengl(WINDOW_SIZE)
    camera = Camera()

    rings = olympic_rings()
    bunny = bunny_world()

    render_loop(camera, WINDOW_SIZE, P, [rings, bunny])


if __name__ == "__main__":
    main()
