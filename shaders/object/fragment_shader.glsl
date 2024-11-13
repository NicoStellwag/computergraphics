#version 130

in vec3 pass_wc_position;
in vec3 pass_normal;
in vec2 pass_texture_coord;
in vec4 pass_color;

out vec4 frag_color;

// texture uniforms
uniform int use_colors;
uniform sampler2D texture_sampler;

// ambient light uniforms
uniform float ambient_light_strength;
uniform vec3 ambient_light_color;

// diffuse light uniforms
uniform vec3 diffuse_light_position;
uniform vec3 diffuse_light_color;

// specular light uniforms
uniform vec3 camera_position;
uniform float specular_light_strength;
uniform float specular_light_shininess;

// reflection uniforms
uniform samplerCube skybox_sampler;
uniform float reflection_strength;

vec3 ambient_light() {
    return ambient_light_strength * ambient_light_color;
}

vec3 diffuse_light(vec3 normed_normal, vec3 light_direction) {
    float sim = max(dot(normed_normal, light_direction), 0.0);
    return diffuse_light_color * sim;
}

vec3 specular_light(vec3 view_direction, vec3 normed_normal, vec3 light_direction) {
    vec3 reflection_direction = reflect(-light_direction, normed_normal);
    float spec = pow(max(dot(view_direction, reflection_direction), 0), specular_light_shininess);
    return specular_light_strength * spec * diffuse_light_color;
}

vec4 object_color() {
    if (use_colors == 1) {
        return pass_color;
    }
    return texture(texture_sampler, pass_texture_coord);
}

vec3 reflection(vec3 view_direction, vec3 normed_normal) {
    // make sure you don't have to set skybox sampler if no reflection
    if (reflection_strength == 0.0) {
        return vec3(0.0);
    }

    vec3 skybox_direction = reflect(-view_direction, normed_normal);
    vec4 reflection_color = texture(skybox_sampler, skybox_direction);
    return reflection_color.rgb;
}

void main() {
    // phong lighting model

    // avoid redundant computation
    vec3 view_direction = normalize(camera_position - pass_wc_position);
    vec3 normed_normal = normalize(pass_normal);
    vec3 light_direction = normalize(diffuse_light_position - pass_wc_position);

    vec3 light = ambient_light() + diffuse_light(normed_normal, light_direction) + specular_light(view_direction, normed_normal, light_direction);
    vec3 reflection = reflection(view_direction, normed_normal);
    vec4 texture_color = object_color();
    vec4 mixed_color = vec4((1.0 - reflection_strength) * texture_color.rgb + reflection_strength * reflection, texture_color.a);
    frag_color = mixed_color * vec4(light, 1.0);
}