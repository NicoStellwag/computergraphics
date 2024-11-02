from OpenGL.GL import *


def create_vbo(shaders, name, data):
    """create a vertex buffer object and set the atrribute pointer,
    assumes the vao is already bound

    Args:
        shader (int): shader program
        name (str): attribute name (must match shader)
        data (np array): data to be stored in the vbo
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
    # glBindBuffer(GL_ARRAY_BUFFER, 0)


def create_vao(model, shaders):
    """create a vao and bind the vbos for a given model

    Args:
        model (Model): model struct
        shader (int): shader program

    Returns:
        int: created vao
    """
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    create_vbo(shaders, "position", model.vertices)
    # create_vbo(shaders, "normal", model.normals)
    if model.texture_coords is not None:
        create_vbo(shaders, "texture_coord", model.texture_coords)
    index_buffer = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, index_buffer)
    glBufferData(
        target=GL_ELEMENT_ARRAY_BUFFER,
        size=model.faces.nbytes,
        data=model.faces,
        usage=GL_STATIC_DRAW,
    )
    glBindVertexArray(0)
    # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    return vao


def create_texture(img):
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

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
    glGenerateMipmap(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, 0)
    return texture
