from dataclasses import dataclass
from OpenGL.GL import *
import pygame

from dataload import Model
from events import handle_events
from geometry import np_to_opengl


@dataclass
class RenderObject:
    model: Model
    vao: int
    shaders: int
    texture: int
    texture_type: int


def draw(render_object, camera, P):
    glUseProgram(render_object.shaders)

    # set texture sampler uniform if needed
    if render_object.texture is not None:
        texture_unit = 0
        sampler_loc = glGetUniformLocation(render_object.shaders, "texture_sampler")
        glUniform1i(sampler_loc, texture_unit)

    # set pvm uniform
    pvm_loc = glGetUniformLocation(render_object.shaders, "PVM")
    pvm = np_to_opengl(P @ camera.V() @ render_object.model.M)
    glUniformMatrix4fv(
        pvm_loc,  #  location
        1,  # count
        GL_FALSE,  # transpose
        pvm,  # value
    )

    if render_object.texture is not None:
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(render_object.texture_type, render_object.texture)

    glBindVertexArray(render_object.vao)
    if render_object.model.faces is not None:
        glDrawElements(
            GL_TRIANGLES,  # mode
            render_object.model.faces.size,  # count
            GL_UNSIGNED_INT,  # type
            None,  # indices
        )
    else:
        glDrawArrays(
            GL_TRIANGLES,  # mode
            0,  # first
            render_object.model.vertices.shape[0],  # count
        )
    glBindVertexArray(0)

    if render_object.texture is not None:
        glBindTexture(GL_TEXTURE_2D, 0)


def render_loop(window_size, camera, P, render_objects):
    running = True
    mouse_mvt = None
    clock = pygame.time.Clock()
    while running:
        running, camera, mouse_mvt = handle_events(
            camera=camera, window_size=window_size, prev_mouse_mvt=mouse_mvt
        )
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for render_object in render_objects:
            draw(render_object, camera, P)
        pygame.display.flip()
        clock.tick(60)
