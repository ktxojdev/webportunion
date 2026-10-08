#include "switch_arm64.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

void switch_cpu_init(SwitchContext* ctx) {
    memset(ctx, 0, sizeof(SwitchContext));
    for (int i = 0; i < SWITCH_MAX_PAGES; ++i) {
        ctx->pages[i] = NULL;
    }
    switch_cpu_reset(ctx);
}

void switch_cpu_reset(SwitchContext* ctx) {
    memset(&ctx->cpu, 0, sizeof(SwitchCPU));
    ctx->cpu.pc = 0x80000000ULL; // Standard Horizon process entry
    ctx->cpu.sp = 0x80080000ULL; // Standard stack pointer
    ctx->cpu.halted = false;
    ctx->kernel.heapBase = 0x81000000ULL;
    ctx->kernel.heapSize = 0x1000000ULL; // 16 MB initial heap
    ctx->kernel.processId = 0x57;
    strcpy(ctx->kernel.lastDebugMessage, "[Horizon OS] Initialized");
    ctx->maxwellQueueCount = 0;
}

uint8_t* switch_mem_get_page(SwitchContext* ctx, uint64_t vaddr, bool allocate) {
    // Map address to sparse page index (using low 28 bits)
    uint32_t page_idx = (uint32_t)((vaddr >> 12) & (SWITCH_MAX_PAGES - 1));
    if (!ctx->pages[page_idx] && allocate) {
        ctx->pages[page_idx] = (uint8_t*)calloc(1, SWITCH_PAGE_SIZE);
    }
    return ctx->pages[page_idx];
}

uint32_t switch_mem_read32(SwitchContext* ctx, uint64_t vaddr) {
    uint8_t* page = switch_mem_get_page(ctx, vaddr, false);
    if (!page) return 0;
    uint32_t offset = (uint32_t)(vaddr & (SWITCH_PAGE_SIZE - 1));
    return *(uint32_t*)(page + offset);
}

uint64_t switch_mem_read64(SwitchContext* ctx, uint64_t vaddr) {
    uint64_t low = switch_mem_read32(ctx, vaddr);
    uint64_t high = switch_mem_read32(ctx, vaddr + 4);
    return low | (high << 32);
}

void switch_mem_write32(SwitchContext* ctx, uint64_t vaddr, uint32_t val) {
    uint8_t* page = switch_mem_get_page(ctx, vaddr, true);
    if (!page) return;
    uint32_t offset = (uint32_t)(vaddr & (SWITCH_PAGE_SIZE - 1));
    *(uint32_t*)(page + offset) = val;
}

void switch_mem_write64(SwitchContext* ctx, uint64_t vaddr, uint64_t val) {
    switch_mem_write32(ctx, vaddr, (uint32_t)(val & 0xFFFFFFFF));
    switch_mem_write32(ctx, vaddr + 4, (uint32_t)(val >> 32));
}

void switch_mem_write_bytes(SwitchContext* ctx, uint64_t vaddr, const uint8_t* src, size_t size) {
    for (size_t i = 0; i < size; ++i) {
        uint64_t addr = vaddr + i;
        uint8_t* page = switch_mem_get_page(ctx, addr, true);
        if (page) {
            uint32_t offset = (uint32_t)(addr & (SWITCH_PAGE_SIZE - 1));
            page[offset] = src[i];
        }
    }
}

void switch_handle_svc(SwitchContext* ctx, uint32_t svc_num) {
    switch (svc_num) {
        case HORIZON_SVC_SET_HEAP_SIZE: {
            uint64_t requested_size = ctx->cpu.x[1];
            ctx->kernel.heapSize = requested_size;
            ctx->cpu.x[0] = 0; // Result: 0 (Success)
            ctx->cpu.x[1] = ctx->kernel.heapBase; // Return out_addr
            snprintf(ctx->kernel.lastDebugMessage, sizeof(ctx->kernel.lastDebugMessage),
                     "[Horizon SVC] svcSetHeapSize: allocated 0x%llX bytes at 0x%llX",
                     (unsigned long long)requested_size, (unsigned long long)ctx->kernel.heapBase);
            break;
        }
        case HORIZON_SVC_QUERY_MEMORY: {
            // x0 = MemoryInfo out, x1 = PageInfo out, x2 = query addr
            ctx->cpu.x[0] = 0; // Success
            break;
        }
        case HORIZON_SVC_SLEEP_THREAD: {
            // Emulate slight thread sleep
            break;
        }
        case HORIZON_SVC_OUTPUT_DEBUG_STRING: {
            // x0 = const char* str, x1 = size_t size
            uint64_t str_addr = ctx->cpu.x[0];
            uint64_t str_len = ctx->cpu.x[1];
            if (str_len > 255) str_len = 255;
            char buf[256];
            for (size_t i = 0; i < str_len; ++i) {
                uint8_t* page = switch_mem_get_page(ctx, str_addr + i, false);
                buf[i] = page ? (char)page[(str_addr + i) & (SWITCH_PAGE_SIZE - 1)] : '\0';
            }
            buf[str_len] = '\0';
            snprintf(ctx->kernel.lastDebugMessage, sizeof(ctx->kernel.lastDebugMessage),
                     "[Horizon Output] %s", buf);
            ctx->cpu.x[0] = 0;
            break;
        }
        case HORIZON_SVC_EXIT_PROCESS: {
            ctx->cpu.halted = true;
            snprintf(ctx->kernel.lastDebugMessage, sizeof(ctx->kernel.lastDebugMessage),
                     "[Horizon OS] Process %u Exited normally", ctx->kernel.processId);
            break;
        }
        default:
            snprintf(ctx->kernel.lastDebugMessage, sizeof(ctx->kernel.lastDebugMessage),
                     "[Horizon SVC] Unimplemented SVC 0x%02X", svc_num);
            ctx->cpu.x[0] = 0; // Default return success stub
            break;
    }
}

void switch_feed_maxwell_packet(SwitchContext* ctx, uint32_t method, uint32_t param) {
    if (ctx->maxwellQueueCount >= 1024) return;
    MaxwellDrawCommand& cmd = ctx->maxwellQueue[ctx->maxwellQueueCount++];
    cmd.method = method;
    cmd.param = param;
    
    if (method == NV9097_SET_CLEAR_COLOR) {
        float r = ((param >> 0) & 0xFF) / 255.0f;
        float g = ((param >> 8) & 0xFF) / 255.0f;
        float b = ((param >> 16) & 0xFF) / 255.0f;
        float a = ((param >> 24) & 0xFF) / 255.0f;
        cmd.clearColor[0] = r;
        cmd.clearColor[1] = g;
        cmd.clearColor[2] = b;
        cmd.clearColor[3] = a;
    } else if (method == NV9097_DRAW_ARRAYS) {
        cmd.vertexCount = param & 0xFFFF;
        cmd.primitiveType = (param >> 16) & 0xF;
    }
}

// ARM64 Condition Check
static bool check_condition(SwitchContext* ctx, uint32_t cond) {
    switch (cond) {
        case 0x0: return ctx->cpu.flagZ;                         // EQ
        case 0x1: return !ctx->cpu.flagZ;                        // NE
        case 0x2: return ctx->cpu.flagC;                         // CS
        case 0x3: return !ctx->cpu.flagC;                        // CC
        case 0x4: return ctx->cpu.flagN;                         // MI
        case 0x5: return !ctx->cpu.flagN;                        // PL
        case 0x6: return ctx->cpu.flagV;                         // VS
        case 0x7: return !ctx->cpu.flagV;                        // VC
        case 0x8: return ctx->cpu.flagC && !ctx->cpu.flagZ;      // HI
        case 0x9: return !ctx->cpu.flagC || ctx->cpu.flagZ;      // LS
        case 0xA: return ctx->cpu.flagN == ctx->cpu.flagV;       // GE
        case 0xB: return ctx->cpu.flagN != ctx->cpu.flagV;       // LT
        case 0xC: return !ctx->cpu.flagZ && (ctx->cpu.flagN == ctx->cpu.flagV); // GT
        case 0xD: return ctx->cpu.flagZ || (ctx->cpu.flagN != ctx->cpu.flagV);  // LE
        case 0xE: return true;                                   // AL
        case 0xF: return true;                                   // NV
    }
    return true;
}

// ARM64 Step Interpreter
bool switch_cpu_step(SwitchContext* ctx) {
    if (ctx->cpu.halted) return false;
    
    uint32_t insn = switch_mem_read32(ctx, ctx->cpu.pc);
    uint64_t current_pc = ctx->cpu.pc;
    ctx->cpu.pc += 4;
    ctx->cpu.totalCycles++;
    
    // NOP (0xD503201F)
    if (insn == 0xD503201F) {
        return true;
    }
    
    // SVC (0xD4000001 with imm16)
    if ((insn & 0xFFE0001F) == 0xD4000001) {
        uint32_t svc_num = (insn >> 5) & 0xFFFF;
        switch_handle_svc(ctx, svc_num);
        return true;
    }
    
    // RET (0xD65F03C0 | (Rn << 5))
    if ((insn & 0xFFFFFC1F) == 0xD65F0000) {
        uint32_t rn = (insn >> 5) & 0x1F;
        ctx->cpu.pc = (rn == 31) ? ctx->cpu.sp : ctx->cpu.x[rn];
        return true;
    }
    
    // BR (0xD61F0000 | (Rn << 5))
    if ((insn & 0xFFFFFC1F) == 0xD61F0000) {
        uint32_t rn = (insn >> 5) & 0x1F;
        ctx->cpu.pc = (rn == 31) ? ctx->cpu.sp : ctx->cpu.x[rn];
        return true;
    }

    // BLR (0xD63F0000 | (Rn << 5))
    if ((insn & 0xFFFFFC1F) == 0xD63F0000) {
        uint32_t rn = (insn >> 5) & 0x1F;
        ctx->cpu.x[30] = ctx->cpu.pc; // LR
        ctx->cpu.pc = (rn == 31) ? ctx->cpu.sp : ctx->cpu.x[rn];
        return true;
    }
    
    // B (Unconditional Branch: 0x14000000)
    if ((insn & 0xFC000000) == 0x14000000) {
        int32_t imm26 = (int32_t)(insn & 0x03FFFFFF);
        if (imm26 & 0x02000000) imm26 |= 0xFC000000; // Sign extend
        ctx->cpu.pc = current_pc + ((int64_t)imm26 * 4);
        return true;
    }

    // BL (Branch with Link: 0x94000000)
    if ((insn & 0xFC000000) == 0x94000000) {
        int32_t imm26 = (int32_t)(insn & 0x03FFFFFF);
        if (imm26 & 0x02000000) imm26 |= 0xFC000000;
        ctx->cpu.x[30] = ctx->cpu.pc;
        ctx->cpu.pc = current_pc + ((int64_t)imm26 * 4);
        return true;
    }

    // B.cond (Conditional Branch: 0x54000000)
    if ((insn & 0xFF000010) == 0x54000000) {
        uint32_t cond = insn & 0x0F;
        if (check_condition(ctx, cond)) {
            int32_t imm19 = (int32_t)((insn >> 5) & 0x7FFFF);
            if (imm19 & 0x40000) imm19 |= 0xFFF80000;
            ctx->cpu.pc = current_pc + ((int64_t)imm19 * 4);
        }
        return true;
    }

    // CBZ / CBNZ (0x34000000 / 0x35000000)
    if ((insn & 0x7E000000) == 0x34000000) {
        bool is_64 = (insn >> 31) & 1;
        bool is_cbnz = (insn >> 24) & 1;
        uint32_t rt = insn & 0x1F;
        uint64_t val = (rt == 31) ? 0 : ctx->cpu.x[rt];
        if (!is_64) val = (uint32_t)val;
        bool taken = is_cbnz ? (val != 0) : (val == 0);
        if (taken) {
            int32_t imm19 = (int32_t)((insn >> 5) & 0x7FFFF);
            if (imm19 & 0x40000) imm19 |= 0xFFF80000;
            ctx->cpu.pc = current_pc + ((int64_t)imm19 * 4);
        }
        return true;
    }

    // MOVZ (Move Wide Immediate: 0x52800000 / 0xD2800000)
    if ((insn & 0x7F800000) == 0x52800000) {
        bool is_64 = (insn >> 31) & 1;
        uint32_t rd = insn & 0x1F;
        uint32_t hw = (insn >> 21) & 0x3;
        uint64_t imm16 = (insn >> 5) & 0xFFFF;
        uint64_t result = imm16 << (hw * 16);
        if (rd != 31) {
            ctx->cpu.x[rd] = is_64 ? result : (uint32_t)result;
        }
        return true;
    }

    // MOVK (0x72800000 / 0xF2800000)
    if ((insn & 0x7F800000) == 0x72800000) {
        bool is_64 = (insn >> 31) & 1;
        uint32_t rd = insn & 0x1F;
        uint32_t hw = (insn >> 21) & 0x3;
        uint64_t imm16 = (insn >> 5) & 0xFFFF;
        if (rd != 31) {
            uint64_t mask = ~((uint64_t)0xFFFF << (hw * 16));
            uint64_t prev = ctx->cpu.x[rd];
            uint64_t result = (prev & mask) | (imm16 << (hw * 16));
            ctx->cpu.x[rd] = is_64 ? result : (uint32_t)result;
        }
        return true;
    }

    // ADD / SUB (Immediate: 0x11000000 / 0x51000000)
    if ((insn & 0x1F000000) == 0x11000000) {
        bool is_64 = (insn >> 31) & 1;
        bool is_sub = (insn >> 30) & 1;
        bool set_flags = (insn >> 29) & 1;
        uint32_t shift = (insn >> 22) & 3;
        uint64_t imm12 = (insn >> 10) & 0xFFF;
        if (shift == 1) imm12 <<= 12;
        uint32_t rn = (insn >> 5) & 0x1F;
        uint32_t rd = insn & 0x1F;
        uint64_t op1 = (rn == 31) ? ctx->cpu.sp : ctx->cpu.x[rn];
        uint64_t res = is_sub ? (op1 - imm12) : (op1 + imm12);
        
        if (set_flags) {
            ctx->cpu.flagZ = (res == 0);
            ctx->cpu.flagN = is_64 ? ((res >> 63) & 1) : ((res >> 31) & 1);
            ctx->cpu.flagC = is_sub ? (op1 >= imm12) : (res < op1);
        }
        if (rd != 31) {
            ctx->cpu.x[rd] = is_64 ? res : (uint32_t)res;
        } else if (!set_flags) {
            ctx->cpu.sp = res;
        }
        return true;
    }

    // LDR / STR (Immediate unsigned offset: 0x39000000)
    if ((insn & 0x3B000000) == 0x39000000) {
        uint32_t size = (insn >> 30) & 3; // 0=8, 1=16, 2=32, 3=64
        bool is_load = (insn >> 22) & 1;
        uint32_t imm12 = (insn >> 10) & 0xFFF;
        uint32_t rn = (insn >> 5) & 0x1F;
        uint32_t rt = insn & 0x1F;
        uint64_t offset = imm12 << size;
        uint64_t base = (rn == 31) ? ctx->cpu.sp : ctx->cpu.x[rn];
        uint64_t vaddr = base + offset;

        if (is_load) {
            uint64_t val = (size == 3) ? switch_mem_read64(ctx, vaddr) : switch_mem_read32(ctx, vaddr);
            if (rt != 31) ctx->cpu.x[rt] = val;
        } else {
            uint64_t val = (rt == 31) ? 0 : ctx->cpu.x[rt];
            if (size == 3) {
                switch_mem_write64(ctx, vaddr, val);
            } else {
                switch_mem_write32(ctx, vaddr, (uint32_t)val);
            }
        }
        return true;
    }

    return true; // Fallthrough
}

uint32_t switch_cpu_run(SwitchContext* ctx, uint32_t max_cycles) {
    uint32_t executed = 0;
    while (executed < max_cycles && !ctx->cpu.halted) {
        if (!switch_cpu_step(ctx)) break;
        executed++;
    }
    return executed;
}
