#version 130

in vec3 position;
in vec3 normal;
in vec2 texture_coord;

out vec3 pass_normal;
out vec2 pass_texture_coord;
out vec3 pass_wc_position;

uniform mat4 PVM;
uniform mat4 M;
uniform mat3 normal_matrix;

void main() {
    // set vertex position
    gl_Position = PVM * vec4(position, 1.0);

    // pass normal in world coordinates
    pass_normal = normal_matrix * normal;

    // pass texture coords
    pass_texture_coord = texture_coord;

    // pass position in world coordinates
    vec4 wc_pos = M * vec4(position, 1.0);
    pass_wc_position = wc_pos.xyz / wc_pos.w;
}
