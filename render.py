from dataclasses import dataclass
from OpenGL.GL import *

from model import Model


@dataclass
class RenderObject:
    model: Model
    vao: int
    shaders: int
    texture: int


def draw(render_object, camera, P):
    glUseProgram(render_object.shaders)

    # set texture sampler uniform if needed
    if render_object.texture is not None:
        texture_unit = 0
        sampler_loc = glGetUniformLocation(render_object.shaders, "texture_sampler")
        glUniform1i(sampler_loc, texture_unit)

    # set pvm uniform
    pvm_loc = glGetUniformLocation(render_object.shaders, "PVM")
    pvm = P @ camera.V() @ render_object.model.M
    glUniformMatrix4fv(
        pvm_loc,  #  location
        1,  # count
        GL_FALSE,  # transpose
        pvm,  # value
    )

    if render_object.texture is not None:
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, render_object.texture)

    glBindVertexArray(render_object.vao)
    glDrawElements(
        GL_TRIANGLES,  # mode
        render_object.model.faces.size,  # count
        GL_UNSIGNED_INT,  # type
        None,  # indices
    )
    glBindVertexArray(0)

    if render_object.texture is not None:
        glBindTexture(GL_TEXTURE_2D, 0)
