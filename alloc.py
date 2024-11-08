from OpenGL.GL import *
from typing import Dict
import numpy as np

from structs import Model, RenderObject, Texture


def create_vbo(shaders: int, name: str, data: np.ndarray):
    """create a vertex buffer object and set the atrribute pointer,
    assumes the vao is already bound

    Args:
        shader (int): shader program
        name (str): attribute name (must match shader)
        data (np array): data to be stored in the vbo

    Returns:
        int: vbo id
    """
    location = glGetAttribLocation(shaders, name)
    vbo = glGenBuffers(1)  # todo destroy them
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(
        target=GL_ARRAY_BUFFER,
        size=data.nbytes,
        data=data,
        usage=GL_STATIC_DRAW,
    )
    glVertexAttribPointer(
        index=location,
        size=data.shape[-1],
        type=GL_FLOAT,
        normalized=GL_FALSE,
        stride=0,
        pointer=ctypes.c_void_p(0),
    )
    glEnableVertexAttribArray(location)
    return vbo


def create_vao(model: Model, shaders: int):
    """create a vao and bind the vbos for a given model

    Args:
        model (Model): model struct
        shader (int): shader program

    Returns:
        Tuple[int, List[int]]: (vao id, vbo ids)
    """
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    vbos = []
    vbos.append(create_vbo(shaders, "position", model.vertices))
    if model.normals is not None:
        vbos.append(create_vbo(shaders, "normal", model.normals))
    if model.texture_coords is not None:
        vbos.append(create_vbo(shaders, "texture_coord", model.texture_coords))
    index_buffer = glGenBuffers(1)
    if model.faces is not None:
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, index_buffer)
        glBufferData(
            target=GL_ELEMENT_ARRAY_BUFFER,
            size=model.faces.nbytes,
            data=model.faces,
            usage=GL_STATIC_DRAW,
        )
    glBindVertexArray(0)
    return vao, vbos


def create_2d_texture(img: np.ndarray, unit: int):
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    glTexImage2D(
        GL_TEXTURE_2D,  # target
        0,  # level
        GL_RGBA,  # internal format
        img.shape[1],  # width
        img.shape[0],  # height
        0,  # border
        GL_RGBA,  # format
        GL_UNSIGNED_BYTE,  # type
        img,  # data
    )
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)  # this or mipmap
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glBindTexture(GL_TEXTURE_2D, 0)
    return Texture(id=tex_id, type=GL_TEXTURE_2D, unit=unit)


def create_cubemap_texture(imgs: Dict[str, np.ndarray], unit: int):
    """create a static cubemap texture

    Args:
        imgs (Dict[str, np array]): dict containing 6 faces already prepared as opengl np arrays

    Returns:
        int: texture id
    """
    tex_id = glGenTextures(1)  # no need for a framebuffer for now
    glBindTexture(GL_TEXTURE_CUBE_MAP, tex_id)
    for i, name in enumerate(["px", "nx", "py", "ny", "pz", "nz"]):
        img = imgs[name]
        glTexImage2D(
            GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,  # target
            0,  # level
            GL_RGBA,  # internal format
            img.shape[1],  # width
            img.shape[0],  # height
            0,  # border
            GL_RGBA,  # format
            GL_UNSIGNED_BYTE,  # type
            img,  # data
        )
    # interpolate texels for fragments
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    # clamp to edge to only sample from correct cube face
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
    glBindTexture(GL_TEXTURE_CUBE_MAP, 0)
    return Texture(id=tex_id, type=GL_TEXTURE_CUBE_MAP, unit=unit)


def destroy_render_object(render_object: RenderObject):
    glDeleteVertexArrays(1, render_object.vao)
    for vbo in render_object.vbos:
        glDeleteBuffers(1, vbo)
    for texture in render_object.textures:
        glDeleteTextures(1, texture.id)
    try:
        glDeleteProgram(render_object.shaders)
    except:
        pass  # shaders might be reused between render objects which causes glDeleteProgram to fail
