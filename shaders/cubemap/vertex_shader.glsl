#version 130

in vec3 position;

out vec3 pass_texture_direction;

uniform mat4 PVM;

void main() {
    // cube is centered at origin and in [-1, 1], so position also acts as texture coordinates
    pass_texture_direction = position; 
    vec4 clip_position = PVM * vec4(position, 1.0);
    // set vertex depth equal to w,
    // so when perspective division (which happens between vertex shader and fragment shader)
    // results in depth 1, the max value
    gl_Position = clip_position.xyww;
}