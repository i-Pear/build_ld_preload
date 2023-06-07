# build_ld_preload

# Usage
1. Fill the functions you want to accelerate into `needed_bypass_functions`
2. Run `python3 build_ld_preload.py`
3. Copy `build_library/preload.so` to `app-elfloader`'s rootfs
4. Run your program `./run.sh -k [kernel_image_path] /lib64/ld-linux-x86-64.so.2 --preload /preload.so /bin/your_program`, or put `LD_PRELOAD=/preload.so` into `posix-environ -> Compiled-in environment variables`
5. For more debug info, put `LD_DEBUG=all` into `posix-environ -> Compiled-in environment variables`
6. This should work for both glibc and Musl loader
