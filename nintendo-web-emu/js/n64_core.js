// Nintendo 64 Recomp Fast3D Display List Processor & 3D N64 Geometry Builder
class N64Core {
    constructor() {
        this.wasm = null;
        this.initialized = false;
        this.vertexCount = 0;
        this.indexCount = 0;
    }

    init(wasmModule) {
        this.wasm = wasmModule;
        this.wasm._n64_init();
        this.initialized = true;
        console.log("[N64Core] WebAssembly Core Initialized.");
    }

    reset() {
        if (!this.initialized) return;
        this.wasm._n64_reset();
    }

    setVertexCache(idx, x, y, z, r, g, b, a) {
        if (!this.initialized) return;
        this.wasm._n64_set_cache_vertex(idx, x, y, z, r, g, b, a);
    }

    executeDisplayList(wordsArray) {
        if (!this.initialized) return;
        const words = new Uint32Array(wordsArray);
        const ptr = this.wasm._malloc(words.byteLength);
        this.wasm.HEAPU32.set(words, ptr / 4);

        this.wasm._n64_exec_dl(ptr, words.length);
        this.wasm._free(ptr);

        this.vertexCount = this.wasm._n64_get_vertex_count();
        this.indexCount = this.wasm._n64_get_index_count();
    }

    getMeshBuffers() {
        if (!this.initialized || this.vertexCount === 0) return null;

        const vPtr = this.wasm._n64_get_vertices_ptr();
        const iPtr = this.wasm._n64_get_indices_ptr();

        // 13 floats per vertex (52 bytes)
        const vertices = new Float32Array(this.wasm.HEAPF32.buffer, vPtr, this.vertexCount * 13);
        const indices = new Uint16Array(this.wasm.HEAPU16.buffer, iPtr, this.indexCount);

        return { vertices, indices };
    }

    // Constructs the iconic 3D Nintendo 64 Logo Display List
    buildN64LogoDisplayList(time) {
        this.reset();

        // Set up ModelView rotation matrix
        const modelMatrix = Mat4.rotateY(Mat4.rotateX(Mat4.identity(), 0.35), time * 1.2);
        const ptr = this.wasm._malloc(64);
        this.wasm.HEAPF32.set(modelMatrix, ptr / 4);
        this.wasm._n64_set_matrix(ptr);
        this.wasm._free(ptr);

        // Preload vertex coordinates into RSP Cache
        // Authentic N64 4-color palette
        const colors = [
            [0.95, 0.15, 0.15, 1.0], // Red
            [0.15, 0.85, 0.25, 1.0], // Green
            [0.15, 0.35, 0.95, 1.0], // Blue
            [0.98, 0.85, 0.15, 1.0]  // Yellow
        ];

        // 8 cube-like corner nodes for pillars
        const corners = [
            [-0.7, -0.7, -0.7], [ 0.7, -0.7, -0.7],
            [ 0.7, -0.7,  0.7], [-0.7, -0.7,  0.7],
            [-0.7,  0.7, -0.7], [ 0.7,  0.7, -0.7],
            [ 0.7,  0.7,  0.7], [-0.7,  0.7,  0.7]
        ];

        for (let i = 0; i < 8; ++i) {
            const col = colors[i % 4];
            this.setVertexCache(i, corners[i][0], corners[i][1], corners[i][2], col[0], col[1], col[2], col[3]);
        }

        // Fast3D Display List Commands
        const dl = [
            // G_GEOMETRYMODE: Set Gouraud smooth shading, Backface culling, Lighting
            (0xD9 << 24), 0x00023200,

            // G_TRI2: Pillar 1 & 2
            (0x06 << 24) | (0 << 16) | (2 << 8) | 4,
            (0 << 16) | (4 << 8) | 6,

            // G_TRI2: Pillar 3 & 4
            (0x06 << 24) | (1 << 16) | (3 << 8) | 5,
            (1 << 16) | (5 << 8) | 7,

            // G_TRI2: Diagonals forming the "N" shape
            (0x06 << 24) | (0 << 16) | (6 << 8) | 2,
            (1 << 16) | (7 << 8) | 3,

            // G_TRI2: Back diagonals
            (0x06 << 24) | (4 << 16) | (2 << 8) | 6,
            (5 << 16) | (3 << 8) | 7,

            // G_TRI2: Top crossbars
            (0x06 << 24) | (4 << 16) | (5 << 8) | 6,
            (4 << 16) | (6 << 8) | 7,

            // G_ENDDL
            (0xDF << 24), 0x00000000
        ];

        this.executeDisplayList(dl);
        return modelMatrix;
    }
}

window.N64Core = N64Core;
