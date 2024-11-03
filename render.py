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


def draw(render_object, camera, P, is_skybox=False):
    # for skybox don't update depth buffer
    if is_skybox:
        glDepthMask(GL_FALSE)

    # bind shaders
    glUseProgram(render_object.shaders)

    # set texture sampler uniform if needed
    if render_object.texture is not None:
        texture_unit = 0
        sampler_loc = glGetUniformLocation(render_object.shaders, "texture_sampler")
        glUniform1i(sampler_loc, texture_unit)

    # set pvm uniform
    pvm_loc = glGetUniformLocation(render_object.shaders, "PVM")
    V = camera.V_no_translation() if is_skybox else camera.V()
    pvm = np_to_opengl(P @ V @ render_object.model.M)
    glUniformMatrix4fv(
        pvm_loc,  #  location
        1,  # count
        GL_FALSE,  # transpose
        pvm,  # value
    )

    # bind texture if needed
    if render_object.texture is not None:
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(render_object.texture_type, render_object.texture)

    # bind vao
    glBindVertexArray(render_object.vao)

    # draw
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

    # unbind vao
    glBindVertexArray(0)

    # unbind texture if needed
    if render_object.texture is not None:
        glBindTexture(render_object.texture_type, 0)

    # if skybox re-enable depth buffer
    if is_skybox:
        glDepthMask(GL_TRUE)


def render_loop(window_size, camera, P, render_objects, skybox):
    running = True
    mouse_mvt = None
    clock = pygame.time.Clock()
    while running:
        running, camera, mouse_mvt = handle_events(
            camera=camera, window_size=window_size, prev_mouse_mvt=mouse_mvt
        )
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw(skybox, camera, P, is_skybox=True)
        for render_object in render_objects:
            draw(render_object, camera, P)
        pygame.display.flip()
        clock.tick(60)
