#pragma once
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define SWITCH_PAGE_SIZE 4096
#define SWITCH_MAX_PAGES 65536 // 256 MB virtual guest memory allocated on demand
#define SWITCH_REGISTER_COUNT 31

// Horizon OS Supervisor Call numbers
#define HORIZON_SVC_SET_HEAP_SIZE       0x01
#define HORIZON_SVC_SET_MEMORY_ATTR     0x03
#define HORIZON_SVC_QUERY_MEMORY        0x06
#define HORIZON_SVC_EXIT_PROCESS        0x07
#define HORIZON_SVC_SLEEP_THREAD        0x09
#define HORIZON_SVC_GET_SYSTEM_TICK     0x10
#define HORIZON_SVC_CONNECT_PORT        0x1F
#define HORIZON_SVC_SEND_SYNC_REQUEST   0x21
#define HORIZON_SVC_OUTPUT_DEBUG_STRING 0x27

// Maxwell 3D Commands
#define NV9097_SET_VIEWPORT_SCALE_X     0x200
#define NV9097_SET_VIEWPORT_SCALE_Y     0x204
#define NV9097_SET_CLEAR_COLOR          0x35C
#define NV9097_CLEAR_SURFACE            0x360
#define NV9097_SET_VERTEX_BUFFER        0x600
#define NV9097_SET_INDEX_BUFFER         0x800
#define NV9097_DRAW_ARRAYS              0x860
#define NV9097_DRAW_INDEXED             0x864

struct MaxwellDrawCommand {
    uint32_t method;
    uint32_t param;
    float clearColor[4];
    uint32_t vertexCount;
    uint32_t primitiveType; // 0 = Triangles, 1 = TriangleStrip, 2 = Points, 3 = Lines
};

struct SwitchCPU {
    uint64_t x[SWITCH_REGISTER_COUNT]; // General Purpose Registers X0-X30
    uint64_t sp;                       // Stack Pointer
    uint64_t pc;                       // Program Counter
    
    // Condition Flags
    bool flagN; // Negative
    bool flagZ; // Zero
    bool flagC; // Carry
    bool flagV; // Overflow
    
    bool halted;
    uint64_t totalCycles;
};

struct SwitchKernel {
    uint64_t heapBase;
    uint64_t heapSize;
    char lastDebugMessage[512];
    uint32_t processId;
};

struct SwitchContext {
    SwitchCPU cpu;
    SwitchKernel kernel;
    uint8_t* pages[SWITCH_MAX_PAGES]; // Sparse page table
    
    MaxwellDrawCommand maxwellQueue[1024];
    uint32_t maxwellQueueCount;
};

void switch_cpu_init(SwitchContext* ctx);
void switch_cpu_reset(SwitchContext* ctx);
uint8_t* switch_mem_get_page(SwitchContext* ctx, uint64_t vaddr, bool allocate);
uint32_t switch_mem_read32(SwitchContext* ctx, uint64_t vaddr);
uint64_t switch_mem_read64(SwitchContext* ctx, uint64_t vaddr);
void switch_mem_write32(SwitchContext* ctx, uint64_t vaddr, uint32_t val);
void switch_mem_write64(SwitchContext* ctx, uint64_t vaddr, uint64_t val);
void switch_mem_write_bytes(SwitchContext* ctx, uint64_t vaddr, const uint8_t* src, size_t size);

bool switch_cpu_step(SwitchContext* ctx);
uint32_t switch_cpu_run(SwitchContext* ctx, uint32_t max_cycles);
void switch_handle_svc(SwitchContext* ctx, uint32_t svc_num);
void switch_feed_maxwell_packet(SwitchContext* ctx, uint32_t method, uint32_t param);
