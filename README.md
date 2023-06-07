# build_ld_preload

# Usage
1. Modify `KERNEL_IMAGE_WITH_DBG` in `build_ld_preload.py` for your own kernel image (with debug symbols)
2. Fill the functions you want to accelerate into `needed_bypass_functions`
3. Run `python3 build_ld_preload.py`
4. Copy `build_library/preload.so` to `app-elfloader`'s rootfs
5. Run your program `./run.sh -k [kernel_image_path] /lib64/ld-linux-x86-64.so.2 --preload /preload.so /bin/your_program` (kernel_image_path here can be stripped), or put `LD_PRELOAD=/preload.so` into `posix-environ -> Compiled-in environment variables`
6. For more debug info, put `LD_DEBUG=all` into `posix-environ -> Compiled-in environment variables`
7. This should work for both glibc and Musl loader
