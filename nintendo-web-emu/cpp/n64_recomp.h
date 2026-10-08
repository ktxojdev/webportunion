#pragma once
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define N64_MAX_VERTICES 2048
#define N64_MAX_INDICES  4096
#define N64_MATRIX_STACK_DEPTH 16

// Fast3D Microcode Opcodes
#define G_NOOP           0x00
#define G_VTX            0x01
#define G_MODIFYVTX      0x02
#define G_CULLDL         0x03
#define G_BRANCH_Z       0x04
#define G_TRI1           0x05
#define G_TRI2           0x06
#define G_LINE3D         0x08
#define G_TEXTURE        0xD7
#define G_POPMTX         0xD8
#define G_GEOMETRYMODE   0xD9
#define G_MTX            0xDA
#define G_MOVEWORD       0xDB
#define G_MOVEMEM        0xDC
#define G_LOAD_UCODE     0xDD
#define G_DL             0xDE
#define G_ENDDL          0xDF
#define G_SETOTHERMODE_L 0xB9
#define G_SETOTHERMODE_H 0xBA
#define G_SETCOMBINE     0xFC
#define G_SETTIMG        0xFD
#define G_SETTILE        0xF5
#define G_LOADTILE       0xF4

struct N64Vertex {
    float x, y, z, w;
    float nx, ny, nz;
    float u, v;
    float r, g, b, a;
};

struct N64Matrix {
    float m[4][4];
};

struct N64RecompState {
    N64Vertex vertexCache[32]; // RSP internal vertex buffer (32 slots)
    
    // Output triangle buffer ready for WebGL 2 / WebGPU draw calls
    N64Vertex outputVertices[N64_MAX_VERTICES];
    uint32_t outputVertexCount;
    
    uint16_t outputIndices[N64_MAX_INDICES];
    uint32_t outputIndexCount;
    
    // Matrix Stack (ModelView)
    N64Matrix matrixStack[N64_MATRIX_STACK_DEPTH];
    int32_t matrixStackTop;
    
    // Projection Matrix
    N64Matrix projectionMatrix;
    
    // RSP State flags
    uint32_t geometryMode;
    bool zBufferEnabled;
    bool cullFront;
    bool cullBack;
    bool smoothShading;
    bool lightingEnabled;
    
    // Texture scale
    float textureScaleS;
    float textureScaleT;
    bool textureEnabled;
};

void n64_recomp_init(N64RecompState* state);
void n64_recomp_reset(N64RecompState* state);
void n64_recomp_execute_dl(N64RecompState* state, const uint32_t* dl, uint32_t wordCount);
void n64_matrix_identity(N64Matrix* out);
void n64_matrix_mult(N64Matrix* out, const N64Matrix* a, const N64Matrix* b);
void n64_transform_vertex(const N64Matrix* mtx, const N64Vertex* in, N64Vertex* out);
