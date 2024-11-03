#version 130

in vec3 position;

out vec3 pass_texture_direction;

uniform mat4 PVM;

void main() {
    // cube is centered at origin and in [-1, 1], so position also acts as texture coordinates
    pass_texture_direction = position; 
    gl_Position = PVM * vec4(position, 1.0);
}