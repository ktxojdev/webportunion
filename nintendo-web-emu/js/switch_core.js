// Nintendo Switch WebAssembly Controller & ARM64 Disassembler
class SwitchCore {
    constructor() {
        this.wasm = null;
        this.initialized = false;
        this.pc = 0x80000000n;
        this.sp = 0x80080000n;
        this.registers = new BigUint64Array(31);
        this.flags = { N: false, Z: false, C: false, V: false };
        this.lastDebug = "[Horizon OS] Offline";
        this.isRunning = false;
    }

    async init(wasmModule) {
        this.wasm = wasmModule;
        this.wasm._switch_init();
        this.initialized = true;
        this.updateState();
        console.log("[SwitchCore] WebAssembly Core Initialized.");
    }

    reset() {
        if (!this.initialized) return;
        this.wasm._switch_reset();
        this.updateState();
    }

    loadBinary(uint8Array, vaddr = 0x80000000n) {
        if (!this.initialized) return;
        const size = uint8Array.length;
        const ptr = this.wasm._malloc(size);
        this.wasm.HEAPU8.set(uint8Array, ptr);
        
        const low = Number(vaddr & 0xFFFFFFFFn);
        const high = Number((vaddr >> 32n) & 0xFFFFFFFFn);
        this.wasm._switch_load_binary(ptr, size, low, high);
        this.wasm._free(ptr);
        
        this.updateState();
    }

    step() {
        if (!this.initialized) return false;
        const res = this.wasm._switch_step();
        this.updateState();
        return res !== 0;
    }

    runCycles(count) {
        if (!this.initialized) return 0;
        const executed = this.wasm._switch_run(count);
        this.updateState();
        return executed;
    }

    updateState() {
        if (!this.initialized) return;
        const pcLow = BigInt(this.wasm._switch_get_pc_low() >>> 0);
        const pcHigh = BigInt(this.wasm._switch_get_pc_high() >>> 0);
        this.pc = (pcHigh << 32n) | pcLow;

        const spLow = BigInt(this.wasm._switch_get_sp_low() >>> 0);
        const spHigh = BigInt(this.wasm._switch_get_sp_high() >>> 0);
        this.sp = (spHigh << 32n) | spLow;

        for (let i = 0; i < 31; ++i) {
            const xLow = BigInt(this.wasm._switch_get_x_low(i) >>> 0);
            const xHigh = BigInt(this.wasm._switch_get_x_high(i) >>> 0);
            this.registers[i] = (xHigh << 32n) | xLow;
        }

        const flagsByte = this.wasm._switch_get_flags();
        this.flags.N = Boolean(flagsByte & (1 << 3));
        this.flags.Z = Boolean(flagsByte & (1 << 2));
        this.flags.C = Boolean(flagsByte & (1 << 1));
        this.flags.V = Boolean(flagsByte & (1 << 0));

        const debugPtr = this.wasm._switch_get_last_debug();
        this.lastDebug = this.wasm.UTF8ToString(debugPtr);
    }

    pushMaxwellCommand(method, param) {
        if (!this.initialized) return;
        this.wasm._switch_push_maxwell_cmd(method, param);
    }

    getMaxwellQueue() {
        if (!this.initialized) return [];
        const count = this.wasm._switch_get_maxwell_count();
        const commands = [];
        for (let i = 0; i < count; ++i) {
            commands.push({
                method: this.wasm._switch_get_maxwell_method(i),
                param: this.wasm._switch_get_maxwell_param(i)
            });
        }
        return commands;
    }

    clearMaxwellQueue() {
        if (!this.initialized) return;
        this.wasm._switch_clear_maxwell_queue();
    }

    // ARM64 Disassembler Helper
    disassembleInsn(insn, pcVal = 0n) {
        if (insn === 0xD503201F) return "NOP";
        if ((insn & 0xFFE0001F) === 0xD4000001) {
            const svcNum = (insn >> 5) & 0xFFFF;
            const names = {
                0x01: "svcSetHeapSize",
                0x03: "svcSetMemoryAttribute",
                0x06: "svcQueryMemory",
                0x07: "svcExitProcess",
                0x09: "svcSleepThread",
                0x27: "svcOutputDebugString"
            };
            return `SVC #0x${svcNum.toString(16).toUpperCase()} (${names[svcNum] || "Unknown SVC"})`;
        }
        if ((insn & 0xFFFFFC1F) === 0xD65F0000) {
            const rn = (insn >> 5) & 0x1F;
            return rn === 30 ? "RET" : `RET X${rn}`;
        }
        if ((insn & 0x7F800000) === 0x52800000) {
            const rd = insn & 0x1F;
            const imm16 = (insn >> 5) & 0xFFFF;
            return `MOVZ X${rd}, #0x${imm16.toString(16).toUpperCase()}`;
        }
        if ((insn & 0x1F000000) === 0x11000000) {
            const isSub = (insn >> 30) & 1;
            const setFlags = (insn >> 29) & 1;
            const imm12 = (insn >> 10) & 0xFFF;
            const rn = (insn >> 5) & 0x1F;
            const rd = insn & 0x1F;
            const op = setFlags ? (isSub ? "SUBS" : "ADDS") : (isSub ? "SUB" : "ADD");
            return `${op} X${rd}, X${rn}, #0x${imm12.toString(16).toUpperCase()}`;
        }
        if ((insn & 0xFC000000) === 0x14000000) {
            let imm26 = insn & 0x03FFFFFF;
            if (imm26 & 0x02000000) imm26 |= ~0x03FFFFFF;
            const target = pcVal + BigInt(imm26 * 4);
            return `B 0x${target.toString(16).toUpperCase()}`;
        }
        return `INSN 0x${insn.toString(16).padStart(8, '0').toUpperCase()}`;
    }

    // Built-in Demo ARM64 Programs
    static getDemoHelloWorld() {
        // Assembled ARM64 code for:
        // 1. MOVZ X0, #0x0040 (ptr to string at 0x80000040)
        // 2. MOVZ X1, #28     (length)
        // 3. SVC  #0x27       (svcOutputDebugString)
        // 4. MOVZ X1, #0x1000 (size 64KB)
        // 5. SVC  #0x01       (svcSetHeapSize)
        // 6. SVC  #0x07       (svcExitProcess)
        const code = new Uint8Array(64);
        const view = new DataView(code.buffer);

        view.setUint32(0,  0xD2800800, true); // MOVZ X0, #0x40 (offset 64)
        view.setUint32(4,  0xD2800381, true); // MOVZ X1, #28
        view.setUint32(8,  0xD40004E1, true); // SVC #0x27 (svcOutputDebugString)
        view.setUint32(12, 0xD2820001, true); // MOVZ X1, #0x1000
        view.setUint32(16, 0xD4000021, true); // SVC #0x01 (svcSetHeapSize)
        view.setUint32(20, 0xD40000E1, true); // SVC #0x07 (svcExitProcess)

        const str = "Nintendo Switch Horizon Web!";
        for (let i = 0; i < str.length; ++i) {
            code[32 + i] = str.charCodeAt(i);
        }
        return code;
    }

    static getDemoFibonacci() {
        // Fibonacci loop on X0, X1, X2
        // X0 = 0
        // X1 = 1
        // loop:
        // ADD X2, X0, X1
        // MOV X0, X1
        // MOV X1, X2
        // B loop
        const code = new Uint8Array(32);
        const view = new DataView(code.buffer);
        view.setUint32(0,  0xD2800000, true); // MOVZ X0, #0
        view.setUint32(4,  0xD2800021, true); // MOVZ X1, #1
        view.setUint32(8,  0x91000402, true); // ADD X2, X0, #1
        view.setUint32(12, 0x91000420, true); // ADD X0, X1, #0
        view.setUint32(16, 0x91000441, true); // ADD X1, X2, #0
        view.setUint32(20, 0x17FFFFFD, true); // B -3 (back to loop)
        return code;
    }
}

window.SwitchCore = SwitchCore;
