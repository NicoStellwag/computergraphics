#version 130

in vec2 pass_texture_coord;

out vec4 frag_color;

uniform sampler2D texture_sampler;

void main() {
    frag_color = texture(texture_sampler, pass_texture_coord);
}