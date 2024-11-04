from OpenGL.GL import *
import pygame
import numpy as np

from events import handle_events
from geometry import np_matrix_to_opengl, V, V_no_translation
from structs import Uniform, RenderObject, Camera
from typing import List, Tuple


def set_uniform(uniform: Uniform, shaders: int):
    loc = glGetUniformLocation(shaders, uniform.name)
    assert loc != -1, f"Uniform {uniform.name} not found in shaders {shaders}"
    if uniform.type == "int":
        glUniform1i(loc, uniform.value)
    elif uniform.type == "mat4":
        glUniformMatrix4fv(
            loc,  # location
            1,  # count
            GL_FALSE,  # transpose
            uniform.value,  # value
        )


def draw(render_object: RenderObject, additional_uniforms: List[Uniform] = None):
    # bind shaders
    glUseProgram(render_object.shaders)

    # set uniforms
    if render_object.uniforms is not None:
        for uniform in render_object.uniforms:
            set_uniform(uniform, render_object.shaders)
    if additional_uniforms is not None:
        for uniform in additional_uniforms:
            set_uniform(uniform, render_object.shaders)

    # bind texture if needed
    if render_object.texture is not None:
        glActiveTexture(render_object.texture_unit)
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


def render_loop(
    window_size: Tuple[int, int],
    camera: Camera,
    p: np.ndarray,
    render_objects: List[RenderObject],
    skybox: RenderObject,
):
    running = True
    mouse_mvt = None
    clock = pygame.time.Clock()
    while running:
        # handle pygame events (update camera params, running)
        running, camera, mouse_mvt = handle_events(
            camera=camera, window_size=window_size, prev_mouse_mvt=mouse_mvt
        )

        # clear color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # draw skybox without updating depth buffer
        glDepthMask(GL_FALSE)
        skybox_pvm_uniform = Uniform(
            name="PVM",
            value=np_matrix_to_opengl(p @ V_no_translation(camera) @ skybox.model.m),
            type="mat4",
        )
        draw(skybox, additional_uniforms=[skybox_pvm_uniform])
        glDepthMask(GL_TRUE)

        # draw all other objects
        for render_object in render_objects:
            pvm_uniform = Uniform(
                name="PVM",
                value=np_matrix_to_opengl(p @ V(camera) @ render_object.model.m),
                type="mat4",
            )
            draw(render_object, additional_uniforms=[pvm_uniform])

        # update display and limit to 60 fps
        pygame.display.flip()
        clock.tick(60)
