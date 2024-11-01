#version 130

in vec3 pass_position;

out vec4 frag_color;

void main() {
    frag_color = vec4(pass_position, 1.0);
}