#version 130

in vec3 position;
// in vec3 normal;
in vec2 texture_coord;

out vec2 pass_texture_coord;

uniform mat4 PVM;

void main() {
    gl_Position = PVM * vec4(position, 1.0);
    pass_texture_coord = texture_coord;
}
