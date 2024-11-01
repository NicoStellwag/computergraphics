#version 130

in vec3 position;
// in vec3 normal;

out vec3 pass_position;

uniform mat4 PVM;

void main() {
    gl_Position = PVM * vec4(position, 1.0);
    pass_position = position;
}
