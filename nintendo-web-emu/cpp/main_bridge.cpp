#include <emscripten.h>
#include <string.h>
#include <stdio.h>
#include "switch_arm64.h"
#include "n64_recomp.h"

static SwitchContext g_switch;
static N64RecompState g_n64;

extern "C" {

// ==========================================
// Nintendo Switch Horizon / ARM64 Exports
// ==========================================

EMSCRIPTEN_KEEPALIVE
void switch_init() {
    switch_cpu_init(&g_switch);
}

EMSCRIPTEN_KEEPALIVE
void switch_reset() {
    switch_cpu_reset(&g_switch);
}

EMSCRIPTEN_KEEPALIVE
void switch_load_binary(const uint8_t* data, uint32_t size, uint32_t vaddr_low, uint32_t vaddr_high) {
    uint64_t vaddr = ((uint64_t)vaddr_high << 32) | vaddr_low;
    switch_mem_write_bytes(&g_switch, vaddr, data, size);
    g_switch.cpu.pc = vaddr;
}

EMSCRIPTEN_KEEPALIVE
int switch_step() {
    return switch_cpu_step(&g_switch) ? 1 : 0;
}

EMSCRIPTEN_KEEPALIVE
uint32_t switch_run(uint32_t cycles) {
    return switch_cpu_run(&g_switch, cycles);
}

EMSCRIPTEN_KEEPALIVE
uint32_t switch_get_x_low(uint32_t idx) {
    if (idx >= SWITCH_REGISTER_COUNT) return 0;
    return (uint32_t)(g_switch.cpu.x[idx] & 0xFFFFFFFF);
}

EMSCRIPTEN_KEEPALIVE
uint32_t switch_get_x_high(uint32_t idx) {
    if (idx >= SWITCH_REGISTER_COUNT) return 0;
    return (uint32_t)(g_switch.cpu.x[idx] >> 32);
}

EMSCRIPTEN_KEEPALIVE
uint32_t switch_get_pc_low() {
    return (uint32_t)(g_switch.cpu.pc & 0xFFFFFFFF);
}

EMSCRIPTEN_KEEPALIVE
uint32_t switch_get_pc_high() {
    return (uint32_t)(g_switch.cpu.pc >> 32);
}

EMSCRIPTEN_KEEPALIVE
uint32_t switch_get_sp_low() {
    return (uint32_t)(g_switch.cpu.sp & 0xFFFFFFFF);
}

EMSCRIPTEN_KEEPALIVE
uint32_t switch_get_sp_high() {
    return (uint32_t)(g_switch.cpu.sp >> 32);
}

EMSCRIPTEN_KEEPALIVE
uint32_t switch_get_flags() {
    uint32_t flags = 0;
    if (g_switch.cpu.flagN) flags |= (1 << 3);
    if (g_switch.cpu.flagZ) flags |= (1 << 2);
    if (g_switch.cpu.flagC) flags |= (1 << 1);
    if (g_switch.cpu.flagV) flags |= (1 << 0);
    return flags;
}

EMSCRIPTEN_KEEPALIVE
const char* switch_get_last_debug() {
    return g_switch.kernel.lastDebugMessage;
}

EMSCRIPTEN_KEEPALIVE
void switch_push_maxwell_cmd(uint32_t method, uint32_t param) {
    switch_feed_maxwell_packet(&g_switch, method, param);
}

EMSCRIPTEN_KEEPALIVE
uint32_t switch_get_maxwell_count() {
    return g_switch.maxwellQueueCount;
}

EMSCRIPTEN_KEEPALIVE
uint32_t switch_get_maxwell_method(uint32_t idx) {
    if (idx >= g_switch.maxwellQueueCount) return 0;
    return g_switch.maxwellQueue[idx].method;
}

EMSCRIPTEN_KEEPALIVE
uint32_t switch_get_maxwell_param(uint32_t idx) {
    if (idx >= g_switch.maxwellQueueCount) return 0;
    return g_switch.maxwellQueue[idx].param;
}

EMSCRIPTEN_KEEPALIVE
void switch_clear_maxwell_queue() {
    g_switch.maxwellQueueCount = 0;
}

// ==========================================
// Nintendo 64 Recomp & Fast3D Exports
// ==========================================

EMSCRIPTEN_KEEPALIVE
void n64_init() {
    n64_recomp_init(&g_n64);
}

EMSCRIPTEN_KEEPALIVE
void n64_reset() {
    n64_recomp_reset(&g_n64);
}

EMSCRIPTEN_KEEPALIVE
void n64_set_cache_vertex(uint32_t idx, float x, float y, float z, float r, float g, float b, float a) {
    if (idx >= 32) return;
    N64Vertex* v = &g_n64.vertexCache[idx];
    v->x = x;
    v->y = y;
    v->z = z;
    v->w = 1.0f;
    v->r = r;
    v->g = g;
    v->b = b;
    v->a = a;
}

EMSCRIPTEN_KEEPALIVE
void n64_set_matrix(const float* mtx16) {
    memcpy(g_n64.matrixStack[g_n64.matrixStackTop].m, mtx16, sizeof(float) * 16);
}

EMSCRIPTEN_KEEPALIVE
void n64_exec_dl(const uint32_t* dl_data, uint32_t words) {
    n64_recomp_execute_dl(&g_n64, dl_data, words);
}

EMSCRIPTEN_KEEPALIVE
uint32_t n64_get_vertex_count() {
    return g_n64.outputVertexCount;
}

EMSCRIPTEN_KEEPALIVE
uint32_t n64_get_index_count() {
    return g_n64.outputIndexCount;
}

EMSCRIPTEN_KEEPALIVE
const float* n64_get_vertices_ptr() {
    return (const float*)g_n64.outputVertices;
}

EMSCRIPTEN_KEEPALIVE
const uint16_t* n64_get_indices_ptr() {
    return g_n64.outputIndices;
}

} // extern "C"
