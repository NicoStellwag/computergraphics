import os

os.environ["SDL_VIDEO_X11_FORCE_EGL"] = "1"  # hack for linux vm on mac

import pygame
from OpenGL.GL import *

from events import handle_events
from geometry import WINDOW_SIZE, P, Camera
from model import load_model
from opengl_utils import create_vao, create_texture
from shaders import compile_shaders
from matutils import poseMatrix


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


def render_loop(camera, model, texture, vao, shaders):
    glUseProgram(shaders)

    texture_unit = 0
    sampler_loc = glGetUniformLocation(shaders, "texture_sampler")
    glUniform1i(sampler_loc, texture_unit)
    pvm_loc = glGetUniformLocation(shaders, "PVM")

    running = True
    mouse_mvt = None
    clock = pygame.time.Clock()
    while running:
        running, camera, mouse_mvt = handle_events(
            camera=camera, window_size=WINDOW_SIZE, prev_mouse_mvt=mouse_mvt
        )

        # clear screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # bind texture
        glActiveTexture(GL_TEXTURE0 + texture_unit)
        glBindTexture(GL_TEXTURE_2D, texture)

        # update pvm uniform
        glUniformMatrix4fv(
            pvm_loc,  #  location
            1,  # count
            GL_FALSE,  # transpose
            P @ camera.V() @ model.M,  # value
        )

        # bind vao and draw
        glBindVertexArray(vao)
        glDrawElements(
            GL_TRIANGLES,  # mode
            model.faces.shape[0] * 3,  # count
            GL_UNSIGNED_INT,  # type
            None,  # indices
        )

        # unbind vao and texture
        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)

        pygame.display.flip()
        clock.tick(60)


def main():
    init_pygame(WINDOW_SIZE)
    init_opengl(WINDOW_SIZE)
    camera = Camera()
    shaders = compile_shaders("textured_model")
    model, texture_img = load_model("models/olympic_rings.glb", M=poseMatrix())
    texture = create_texture(texture_img)
    vao = create_vao(model, shaders)

    render_loop(camera, model, texture, vao, shaders)


if __name__ == "__main__":
    main()
