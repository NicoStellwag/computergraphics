from pathlib import Path
from OpenGL.GL import shaders as gl_shaders
from OpenGL.GL import *
from OpenGL.GL.ARB import separate_shader_objects, get_program_binary


def compile_program(*shaders, **named):
    """custom compile program function,
    mostly stolen from OpenGL.GL.shaders.compileProgram,
    but with hack to make shaders with multiple texture samplers work

    Returns:
        int: shader program
    """
    program = glCreateProgram()
    if named.get("separable"):
        glProgramParameteri(
            program, separate_shader_objects.GL_PROGRAM_SEPARABLE, GL_TRUE
        )
    if named.get("retrievable"):
        glProgramParameteri(
            program, get_program_binary.GL_PROGRAM_BINARY_RETRIEVABLE_HINT, GL_TRUE
        )
    for shader in shaders:
        glAttachShader(program, shader)
    program = gl_shaders.ShaderProgram(program)
    glLinkProgram(program)
    if named[
        "set_texture_units"
    ]:  # * make validate work with multiple texture samplers
        glUseProgram(program)
        glUniform1i(glGetUniformLocation(program, "texture_sampler"), 0)
        glUniform1i(glGetUniformLocation(program, "skybox_sampler"), 1)
        glUseProgram(0)
    if named.get("validate", True):
        program.check_validate()
    program.check_linked()
    for shader in shaders:
        glDeleteShader(shader)
    return program


def compile_shaders(shaders_name):
    shaders_dir = Path("shaders") / shaders_name
    vertex_shader_file = shaders_dir / "vertex_shader.glsl"
    fragment_shader_file = shaders_dir / "fragment_shader.glsl"
    vertex_shader_code = vertex_shader_file.read_text()
    fragment_shader_code = fragment_shader_file.read_text()
    program = compile_program(
        gl_shaders.compileShader(vertex_shader_code, GL_VERTEX_SHADER),
        gl_shaders.compileShader(fragment_shader_code, GL_FRAGMENT_SHADER),
        set_texture_units=True,
    )
    return program
