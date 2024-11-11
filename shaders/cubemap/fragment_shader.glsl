# version 130

in vec3 pass_texture_direction;

out vec4 frac_color;

uniform samplerCube skybox_sampler;

void main() {
    frac_color = texture(skybox_sampler, pass_texture_direction);
}