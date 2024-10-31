from pathlib import Path
from OpenGL.GL import shaders, GL_VERTEX_SHADER, GL_FRAGMENT_SHADER


def compile_shaders(shaders_name):
    shaders_dir = Path("shaders") / shaders_name
    vertex_shader_file = shaders_dir / "vertex_shader.glsl"
    fragment_shader_file = shaders_dir / "fragment_shader.glsl"
    vertex_shader_code = vertex_shader_file.read_text()
    fragment_shader_code = fragment_shader_file.read_text()
    program = shaders.compileProgram(
        shaders.compileShader(vertex_shader_code, GL_VERTEX_SHADER),
        shaders.compileShader(fragment_shader_code, GL_FRAGMENT_SHADER),
    )
    return program
