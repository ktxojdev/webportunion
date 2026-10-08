// Nintendo 64 Fast3D Recomp WebGL 2 Hardware Renderer
class N64Renderer {
    constructor() {
        this.canvas = null;
        this.gl = null;
        this.program = null;
        this.vbo = null;
        this.ibo = null;

        this.uMVP = null;
        this.uModel = null;
        this.uLightDir = null;
        this.uShadingMode = null; // 0 = Gouraud, 1 = Flat, 2 = Wireframe

        this.zBuffer = true;
        this.cullFace = true;
        this.wireframe = false;
    }

    init(canvas) {
        this.canvas = canvas;
        const gl = canvas.getContext('webgl2', { alpha: false, depth: true, antialias: true });
        if (!gl) {
            console.error("[N64 Fast3D] WebGL2 not supported.");
            return false;
        }
        this.gl = gl;

        const vsSrc = `#version 300 es
            layout(location = 0) in vec4 aPosition;
            layout(location = 1) in vec3 aNormal;
            layout(location = 2) in vec2 aUV;
            layout(location = 3) in vec4 aColor;

            uniform mat4 uMVP;
            uniform mat4 uModel;
            uniform vec3 uLightDir;

            out vec4 vColor;
            out vec2 vUV;

            void main() {
                gl_Position = uMVP * vec4(aPosition.xyz, 1.0);
                
                // N64 Hardware RSP Lighting calculation
                vec3 norm = normalize(mat3(uModel) * aNormal);
                float diff = max(dot(norm, normalize(uLightDir)), 0.0);
                float ambient = 0.35;
                float intensity = clamp(ambient + diff * 0.75, 0.0, 1.0);

                vColor = vec4(aColor.rgb * intensity, aColor.a);
                vUV = aUV;
            }
        `;

        const fsSrc = `#version 300 es
            precision mediump float;
            in vec4 vColor;
            in vec2 vUV;
            out vec4 fragColor;

            void main() {
                fragColor = vColor;
            }
        `;

        const vs = gl.createShader(gl.VERTEX_SHADER);
        gl.shaderSource(vs, vsSrc);
        gl.compileShader(vs);

        const fs = gl.createShader(gl.FRAGMENT_SHADER);
        gl.shaderSource(fs, fsSrc);
        gl.compileShader(fs);

        const prog = gl.createProgram();
        gl.attachShader(prog, vs);
        gl.attachShader(prog, fs);
        gl.linkProgram(prog);
        this.program = prog;

        this.uMVP = gl.getUniformLocation(prog, "uMVP");
        this.uModel = gl.getUniformLocation(prog, "uModel");
        this.uLightDir = gl.getUniformLocation(prog, "uLightDir");

        this.vbo = gl.createBuffer();
        this.ibo = gl.createBuffer();

        console.log("[N64 Fast3D] WebGL2 Pipeline initialized.");
        return true;
    }

    render(vertexData, indexData, mvpMatrix, modelMatrix, lightDir) {
        const gl = this.gl;
        if (!gl || !this.program) return;

        gl.viewport(0, 0, this.canvas.width, this.canvas.height);
        gl.clearColor(0.08, 0.09, 0.11, 1.0);

        if (this.zBuffer) {
            gl.enable(gl.DEPTH_TEST);
            gl.depthFunc(gl.LEQUAL);
        } else {
            gl.disable(gl.DEPTH_TEST);
        }

        if (this.cullFace) {
            gl.enable(gl.CULL_FACE);
            gl.cullFace(gl.BACK);
        } else {
            gl.disable(gl.CULL_FACE);
        }

        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

        gl.useProgram(this.program);
        gl.uniformMatrix4fv(this.uMVP, false, mvpMatrix);
        gl.uniformMatrix4fv(this.uModel, false, modelMatrix);
        gl.uniform3fv(this.uLightDir, lightDir || [0.577, 0.577, 0.577]);

        // Upload and bind vertices
        gl.bindBuffer(gl.ARRAY_BUFFER, this.vbo);
        gl.bufferData(gl.ARRAY_BUFFER, vertexData, gl.DYNAMIC_DRAW);

        // N64Vertex layout:
        // x, y, z, w (4 floats = 16 bytes)
        // nx, ny, nz (3 floats = 12 bytes)
        // u, v       (2 floats = 8 bytes)
        // r, g, b, a (4 floats = 16 bytes)
        // Total stride = 13 floats * 4 bytes = 52 bytes
        const stride = 52;

        gl.enableVertexAttribArray(0); // Position
        gl.vertexAttribPointer(0, 4, gl.FLOAT, false, stride, 0);

        gl.enableVertexAttribArray(1); // Normal
        gl.vertexAttribPointer(1, 3, gl.FLOAT, false, stride, 16);

        gl.enableVertexAttribArray(2); // UV
        gl.vertexAttribPointer(2, 2, gl.FLOAT, false, stride, 28);

        gl.enableVertexAttribArray(3); // Color
        gl.vertexAttribPointer(3, 4, gl.FLOAT, false, stride, 36);

        // Upload and bind indices
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this.ibo);
        gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, indexData, gl.DYNAMIC_DRAW);

        const mode = this.wireframe ? gl.LINES : gl.TRIANGLES;
        gl.drawElements(mode, indexData.length, gl.UNSIGNED_SHORT, 0);
    }
}

window.N64Renderer = N64Renderer;
