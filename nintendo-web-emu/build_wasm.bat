@echo off
setlocal
cd /d "%~dp0"

echo [1/3] Setting up Emscripten SDK Environment...
call "..\HNPort\toolchain\emsdk\emsdk_env.bat"

echo [2/3] Compiling Nintendo Web Emulator Core (Switch ARM64 + N64 Recomp Fast3D)...
call em++ -O3 -std=c++17 ^
    "cpp\switch_arm64.cpp" ^
    "cpp\n64_recomp.cpp" ^
    "cpp\main_bridge.cpp" ^
    -s WASM=1 ^
    -s EXPORT_ES6=0 ^
    -s MODULARIZE=1 ^
    -s "EXPORT_NAME='NintendoEmuModule'" ^
    -s ALLOW_MEMORY_GROWTH=1 ^
    -s "EXPORTED_FUNCTIONS=['_switch_init','_switch_reset','_switch_load_binary','_switch_step','_switch_run','_switch_get_x_low','_switch_get_x_high','_switch_get_pc_low','_switch_get_pc_high','_switch_get_sp_low','_switch_get_sp_high','_switch_get_flags','_switch_get_last_debug','_switch_push_maxwell_cmd','_switch_get_maxwell_count','_switch_get_maxwell_method','_switch_get_maxwell_param','_switch_clear_maxwell_queue','_n64_init','_n64_reset','_n64_set_cache_vertex','_n64_set_matrix','_n64_exec_dl','_n64_get_vertex_count','_n64_get_index_count','_n64_get_vertices_ptr','_n64_get_indices_ptr','_malloc','_free']" ^
    -s "EXPORTED_RUNTIME_METHODS=['ccall','cwrap','HEAPU8','HEAP32','HEAPF32','HEAPU16']" ^
    -o "emu_core.js"

if %ERRORLEVEL% EQU 0 (
    echo [3/3] SUCCESS! emu_core.js and emu_core.wasm generated successfully!
) else (
    echo [ERROR] WebAssembly compilation failed with code %ERRORLEVEL%
)
