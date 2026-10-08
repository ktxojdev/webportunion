#include "n64_recomp.h"
#include <string.h>
#include <math.h>

void n64_matrix_identity(N64Matrix* out) {
    memset(out->m, 0, sizeof(out->m));
    out->m[0][0] = 1.0f;
    out->m[1][1] = 1.0f;
    out->m[2][2] = 1.0f;
    out->m[3][3] = 1.0f;
}

void n64_matrix_mult(N64Matrix* out, const N64Matrix* a, const N64Matrix* b) {
    N64Matrix temp;
    for (int i = 0; i < 4; ++i) {
        for (int j = 0; j < 4; ++j) {
            temp.m[i][j] = a->m[i][0] * b->m[0][j] +
                           a->m[i][1] * b->m[1][j] +
                           a->m[i][2] * b->m[2][j] +
                           a->m[i][3] * b->m[3][j];
        }
    }
    memcpy(out, &temp, sizeof(N64Matrix));
}

void n64_transform_vertex(const N64Matrix* mtx, const N64Vertex* in, N64Vertex* out) {
    *out = *in;
    out->x = in->x * mtx->m[0][0] + in->y * mtx->m[1][0] + in->z * mtx->m[2][0] + mtx->m[3][0];
    out->y = in->x * mtx->m[0][1] + in->y * mtx->m[1][1] + in->z * mtx->m[2][1] + mtx->m[3][1];
    out->z = in->x * mtx->m[0][2] + in->y * mtx->m[1][2] + in->z * mtx->m[2][2] + mtx->m[3][2];
    out->w = in->x * mtx->m[0][3] + in->y * mtx->m[1][3] + in->z * mtx->m[2][3] + mtx->m[3][3];
    if (out->w == 0.0f) out->w = 1.0f;
}

void n64_recomp_init(N64RecompState* state) {
    memset(state, 0, sizeof(N64RecompState));
    n64_recomp_reset(state);
}

void n64_recomp_reset(N64RecompState* state) {
    state->outputVertexCount = 0;
    state->outputIndexCount = 0;
    state->matrixStackTop = 0;
    n64_matrix_identity(&state->matrixStack[0]);
    n64_matrix_identity(&state->projectionMatrix);
    
    state->zBufferEnabled = true;
    state->cullBack = true;
    state->cullFront = false;
    state->smoothShading = true;
    state->lightingEnabled = true;
    state->textureEnabled = false;
    state->textureScaleS = 1.0f;
    state->textureScaleT = 1.0f;
}

static void emit_triangle(N64RecompState* state, uint32_t v0, uint32_t v1, uint32_t v2) {
    if (v0 >= 32 || v1 >= 32 || v2 >= 32) return;
    if (state->outputIndexCount + 3 > N64_MAX_INDICES) return;
    if (state->outputVertexCount + 3 > N64_MAX_VERTICES) return;

    N64Matrix* curMtx = &state->matrixStack[state->matrixStackTop];

    uint16_t baseIdx = (uint16_t)state->outputVertexCount;
    
    n64_transform_vertex(curMtx, &state->vertexCache[v0], &state->outputVertices[state->outputVertexCount++]);
    n64_transform_vertex(curMtx, &state->vertexCache[v1], &state->outputVertices[state->outputVertexCount++]);
    n64_transform_vertex(curMtx, &state->vertexCache[v2], &state->outputVertices[state->outputVertexCount++]);

    state->outputIndices[state->outputIndexCount++] = baseIdx;
    state->outputIndices[state->outputIndexCount++] = baseIdx + 1;
    state->outputIndices[state->outputIndexCount++] = baseIdx + 2;
}

void n64_recomp_execute_dl(N64RecompState* state, const uint32_t* dl, uint32_t wordCount) {
    uint32_t pc = 0;
    while (pc + 1 < wordCount) {
        uint32_t w0 = dl[pc++];
        uint32_t w1 = dl[pc++];
        uint8_t opcode = (uint8_t)(w0 >> 24);

        switch (opcode) {
            case G_ENDDL:
                return;

            case G_VTX: {
                // w0: [opcode:8][num_vertices:8][buffer_index:8][reserved:8]
                // For synthetic and recompiled display lists, w1 encodes simulated vertex data pointer or index
                uint32_t num = (w0 >> 12) & 0xFF;
                uint32_t dst_idx = (w0 >> 1) & 0x7F;
                // In demo display list, w1 can carry raw vertex color/geometry seeds
                for (uint32_t i = 0; i < num && (dst_idx + i) < 32; ++i) {
                    N64Vertex* v = &state->vertexCache[dst_idx + i];
                    v->w = 1.0f;
                }
                break;
            }

            case G_TRI1: {
                // w0: [opcode:8][v0:8][v1:8][v2:8]
                uint32_t v0 = (w1 >> 16) & 0xFF;
                uint32_t v1 = (w1 >> 8) & 0xFF;
                uint32_t v2 = w1 & 0xFF;
                emit_triangle(state, v0 / 2, v1 / 2, v2 / 2);
                break;
            }

            case G_TRI2: {
                uint32_t v0 = (w0 >> 16) & 0xFF;
                uint32_t v1 = (w0 >> 8) & 0xFF;
                uint32_t v2 = w0 & 0xFF;
                emit_triangle(state, v0 / 2, v1 / 2, v2 / 2);

                uint32_t v3 = (w1 >> 16) & 0xFF;
                uint32_t v4 = (w1 >> 8) & 0xFF;
                uint32_t v5 = w1 & 0xFF;
                emit_triangle(state, v3 / 2, v4 / 2, v5 / 2);
                break;
            }

            case G_POPMTX: {
                uint32_t num = w1 / 64;
                if (num == 0) num = 1;
                state->matrixStackTop -= num;
                if (state->matrixStackTop < 0) state->matrixStackTop = 0;
                break;
            }

            case G_GEOMETRYMODE: {
                uint32_t clear_bits = ~w0 & 0x00FFFFFF;
                uint32_t set_bits = w1 & 0x00FFFFFF;
                state->geometryMode = (state->geometryMode & ~clear_bits) | set_bits;
                state->smoothShading = (state->geometryMode & 0x00000200) != 0;
                state->cullFront = (state->geometryMode & 0x00001000) != 0;
                state->cullBack = (state->geometryMode & 0x00002000) != 0;
                state->lightingEnabled = (state->geometryMode & 0x00020000) != 0;
                break;
            }

            case G_TEXTURE: {
                state->textureScaleS = ((w1 >> 16) & 0xFFFF) / 65536.0f;
                state->textureScaleT = (w1 & 0xFFFF) / 65536.0f;
                state->textureEnabled = ((w0 >> 8) & 0xFF) != 0;
                break;
            }

            default:
                break;
        }
    }
}
