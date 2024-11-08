#version 130

in vec3 pass_wc_position;
in vec3 pass_normal;
in vec2 pass_texture_coord;

out vec4 frag_color;

uniform sampler2D texture_sampler;
uniform float ambient_light_strength;
uniform vec3 ambient_light_color;
uniform vec3 diffuse_light_position;
uniform vec3 diffuse_light_color;
uniform vec3 camera_position;
uniform float specular_light_strength;
uniform float specular_light_shininess;

vec3 ambient_light() {
    return ambient_light_strength * ambient_light_color;
}

vec3 diffuse_light() {
    vec3 normed_normal = normalize(pass_normal);
    vec3 light_direction = normalize(diffuse_light_position - pass_wc_position);
    float sim = max(dot(normed_normal, light_direction), 0.0);
    return diffuse_light_color * sim;
}

vec3 specular_light() {
    vec3 normed_normal = normalize(pass_normal);
    vec3 view_direction = normalize(camera_position - pass_wc_position);
    vec3 light_direction = normalize(diffuse_light_position - pass_wc_position);
    vec3 reflection_direction = reflect(-light_direction, normed_normal);
    float spec = pow(max(dot(view_direction, reflection_direction), 0), specular_light_shininess);
    return specular_light_strength * spec * diffuse_light_color;
}

vec4 object_color() {
    return texture(texture_sampler, pass_texture_coord);
}

void main() {
    vec3 light = ambient_light() + diffuse_light() + specular_light();
    frag_color = object_color() * vec4(light, 1.0);
}