// Nintendo Switch Maxwell 3D / WebGPU & WebGL 2 Translation Pipeline
class SwitchRenderer {
    constructor() {
        this.canvas = null;
        this.backend = 'none'; // 'webgpu' or 'webgl2'
        
        // WebGPU handles
        this.device = null;
        this.gpuContext = null;
        this.pipeline = null;
        this.gpuVertexBuffer = null;
        this.gpuUniformBuffer = null;
        this.bindGroup = null;

        // WebGL2 handles
        this.gl = null;
        this.program = null;
        this.vbo = null;
        this.uMatrix = null;
        this.uColor = null;

        this.clearColor = [0.12, 0.13, 0.15, 1.0];
    }

    async init(canvas) {
        this.canvas = canvas;

        // 1. Attempt WebGPU initialization first
        if (navigator.gpu) {
            try {
                const adapter = await navigator.gpu.requestAdapter();
                if (adapter) {
                    this.device = await adapter.requestDevice();
                    this.gpuContext = this.canvas.getContext('webgpu');
                    const format = navigator.gpu.getPreferredCanvasFormat();
                    this.gpuContext.configure({
                        device: this.device,
                        format: format,
                        alphaMode: 'opaque'
                    });
                    await this.initWebGPU(format);
                    this.backend = 'webgpu';
                    console.log("[Switch Maxwell] WebGPU Pipeline initialized successfully.");
                    return 'webgpu';
                }
            } catch (err) {
                console.warn("[Switch Maxwell] WebGPU init failed, falling back to WebGL2:", err);
            }
        }

        // 2. WebGL 2 Fallback
        this.gl = this.canvas.getContext('webgl2', { alpha: false, depth: true, antialias: true });
        if (this.gl) {
            this.initWebGL2();
            this.backend = 'webgl2';
            console.log("[Switch Maxwell] WebGL 2 Pipeline initialized successfully.");
            return 'webgl2';
        }

        console.error("[Switch Maxwell] Neither WebGPU nor WebGL2 supported.");
        return 'unsupported';
    }

    async initWebGPU(format) {
        const wgslShader = `
            struct Uniforms {
                modelViewProj: mat4x4<f32>,
                lightColor: vec4<f32>,
            };
            @binding(0) @group(0) var<uniform> uniforms: Uniforms;

            struct VertexInput {
                @location(0) position: vec3<f32>,
                @location(1) color: vec4<f32>,
            };

            struct VertexOutput {
                @builtin(position) position: vec4<f32>,
                @location(0) color: vec4<f32>,
            };

            @vertex
            fn vs_main(in: VertexInput) -> VertexOutput {
                var out: VertexOutput;
                out.position = uniforms.modelViewProj * vec4<f32>(in.position, 1.0);
                out.color = in.color;
                return out;
            }

            @fragment
            fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
                return in.color;
            }
        `;

        const shaderModule = this.device.createShaderModule({ code: wgslShader });

        this.pipeline = this.device.createRenderPipeline({
            layout: 'auto',
            vertex: {
                module: shaderModule,
                entryPoint: 'vs_main',
                buffers: [{
                    arrayStride: 28, // 3 floats (pos) + 4 floats (color) = 7 * 4 = 28 bytes
                    attributes: [
                        { shaderLocation: 0, offset: 0, format: 'float32x3' },
                        { shaderLocation: 1, offset: 12, format: 'float32x4' },
                    ]
                }]
            },
            fragment: {
                module: shaderModule,
                entryPoint: 'fs_main',
                targets: [{ format: format }]
            },
            primitive: {
                topology: 'triangle-list',
                cullMode: 'none'
            },
            depthStencil: {
                depthWriteEnabled: true,
                depthCompare: 'less',
                format: 'depth24plus'
            }
        });

        this.depthTexture = this.device.createTexture({
            size: [this.canvas.width, this.canvas.height],
            format: 'depth24plus',
            usage: GPUTextureUsage.RENDER_ATTACHMENT
        });

        this.gpuUniformBuffer = this.device.createBuffer({
            size: 80, // mat4 (64) + vec4 (16)
            usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST
        });

        this.bindGroup = this.device.createBindGroup({
            layout: this.pipeline.getBindGroupLayout(0),
            entries: [{ binding: 0, resource: { buffer: this.gpuUniformBuffer } }]
        });
    }

    initWebGL2() {
        const gl = this.gl;
        const vsSrc = `#version 300 es
            layout(location = 0) in vec3 aPos;
            layout(location = 1) in vec4 aColor;
            uniform mat4 uMVP;
            out vec4 vColor;
            void main() {
                gl_Position = uMVP * vec4(aPos, 1.0);
                vColor = aColor;
            }
        `;

        const fsSrc = `#version 300 es
            precision mediump float;
            in vec4 vColor;
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

        this.uMatrix = gl.getUniformLocation(prog, "uMVP");
        this.vbo = gl.createBuffer();
    }

    setClearColor(r, g, b, a) {
        this.clearColor = [r, g, b, a];
    }

    // Renders Maxwell 3D Joy-Con / Switch geometry
    renderFrame(geometryVertices, mvpMatrix) {
        if (this.backend === 'webgpu') {
            this.renderWebGPU(geometryVertices, mvpMatrix);
        } else if (this.backend === 'webgl2') {
            this.renderWebGL2(geometryVertices, mvpMatrix);
        }
    }

    renderWebGPU(vertices, mvpMatrix) {
        if (!this.device || !this.gpuContext) return;

        // Upload uniforms
        const uniformData = new Float32Array(20);
        uniformData.set(mvpMatrix, 0);
        uniformData.set([1, 1, 1, 1], 16);
        this.device.queue.writeBuffer(this.gpuUniformBuffer, 0, uniformData);

        // Upload vertex buffer
        if (!this.gpuVertexBuffer || this.gpuVertexBuffer.size < vertices.byteLength) {
            if (this.gpuVertexBuffer) this.gpuVertexBuffer.destroy();
            this.gpuVertexBuffer = this.device.createBuffer({
                size: Math.max(vertices.byteLength, 65536),
                usage: GPUBufferUsage.VERTEX | GPUBufferUsage.COPY_DST
            });
        }
        this.device.queue.writeBuffer(this.gpuVertexBuffer, 0, vertices);

        const commandEncoder = this.device.createCommandEncoder();
        const renderPass = commandEncoder.beginRenderPass({
            colorAttachments: [{
                view: this.gpuContext.getCurrentTexture().createView(),
                clearValue: { r: this.clearColor[0], g: this.clearColor[1], b: this.clearColor[2], a: this.clearColor[3] },
                loadOp: 'clear',
                storeOp: 'store'
            }],
            depthStencilAttachment: {
                view: this.depthTexture.createView(),
                depthClearValue: 1.0,
                depthLoadOp: 'clear',
                depthStoreOp: 'store'
            }
        });

        renderPass.setPipeline(this.pipeline);
        renderPass.setBindGroup(0, this.bindGroup);
        renderPass.setVertexBuffer(0, this.gpuVertexBuffer);
        renderPass.draw(vertices.length / 7, 1, 0, 0);
        renderPass.end();

        this.device.queue.submit([commandEncoder.finish()]);
    }

    renderWebGL2(vertices, mvpMatrix) {
        const gl = this.gl;
        if (!gl) return;

        gl.viewport(0, 0, this.canvas.width, this.canvas.height);
        gl.clearColor(this.clearColor[0], this.clearColor[1], this.clearColor[2], this.clearColor[3]);
        gl.enable(gl.DEPTH_TEST);
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

        gl.useProgram(this.program);
        gl.uniformMatrix4fv(this.uMatrix, false, mvpMatrix);

        gl.bindBuffer(gl.ARRAY_BUFFER, this.vbo);
        gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.DYNAMIC_DRAW);

        const stride = 28; // 7 floats * 4 bytes
        gl.enableVertexAttribArray(0); // Pos (vec3)
        gl.vertexAttribPointer(0, 3, gl.FLOAT, false, stride, 0);

        gl.enableVertexAttribArray(1); // Color (vec4)
        gl.vertexAttribPointer(1, 4, gl.FLOAT, false, stride, 12);

        gl.drawArrays(gl.TRIANGLES, 0, vertices.length / 7);
    }
}

window.SwitchRenderer = SwitchRenderer;
