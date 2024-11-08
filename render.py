from OpenGL.GL import *
import pygame
import numpy as np

from events import handle_events
from geometry import np_matrix_to_opengl, V, V_no_translation, camera_position
from structs import Uniform, RenderObject, Camera
from typing import List, Tuple


def set_uniform(uniform: Uniform, shaders: int):
    loc = glGetUniformLocation(shaders, uniform.name)
    assert loc != -1, f"Uniform {uniform.name} not found in shaders {shaders}"
    if uniform.type == "int":
        glUniform1i(loc, uniform.value)
    elif uniform.type == "float":
        glUniform1f(loc, uniform.value)
    elif uniform.type == "vec3":
        glUniform3f(loc, *uniform.value)
    elif uniform.type == "mat3":
        glUniformMatrix3fv(
            loc,  # location
            1,  # count
            GL_FALSE,  # transpose
            uniform.value,  # value
        )
    elif uniform.type == "mat4":
        glUniformMatrix4fv(
            loc,  # location
            1,  # count
            GL_FALSE,  # transpose
            uniform.value,  # value
        )


def draw(render_object: RenderObject, dynamic_uniforms: List[Uniform] = None):
    # bind shaders
    glUseProgram(render_object.shaders)

    # set uniforms
    if render_object.static_uniforms is not None:
        for uniform in render_object.static_uniforms:
            set_uniform(uniform, render_object.shaders)
    if dynamic_uniforms is not None:
        for uniform in dynamic_uniforms:
            set_uniform(uniform, render_object.shaders)

    # bind textures if needed
    if render_object.textures is not None:
        for texture in render_object.textures:
            glActiveTexture(texture.unit)
            glBindTexture(texture.type, texture.id)

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

    # unbind textures if needed
    if render_object.textures is not None:
        for texture in render_object.textures:
            glBindTexture(texture.type, 0)


def render_loop(
    window_size: Tuple[int, int],
    camera: Camera,
    p: np.ndarray,
    objects: List[RenderObject],
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

        # draw objects
        camera_pos_uniform = Uniform(
            name="camera_position",
            value=camera_position(camera).tolist(),
            type="vec3",
        )
        for render_object in objects:
            pvm_uniform = Uniform(
                name="PVM",
                value=np_matrix_to_opengl(p @ V(camera) @ render_object.model.m),
                type="mat4",
            )
            draw(render_object, dynamic_uniforms=[pvm_uniform, camera_pos_uniform])

        # draw skybox
        # no idea why you would want to draw the skybox when
        # there's an object with z = 1.0 in NDC,
        # but people seem to do it that way
        glDepthFunc(GL_LEQUAL)
        skybox_pvm_uniform = Uniform(
            name="PVM",
            value=np_matrix_to_opengl(p @ V_no_translation(camera) @ skybox.model.m),
            type="mat4",
        )
        draw(skybox, dynamic_uniforms=[skybox_pvm_uniform])
        glDepthFunc(GL_LESS)

        # update display and limit to 60 fps
        pygame.display.flip()
        clock.tick(60)
