#define ADAPT(func_name) void func_name () { \
asm("jmp *(%rip)"); \
asm("nop"); \
asm("nop"); \
asm("nop"); \
asm("nop"); \
asm("nop"); \
asm("nop"); \
asm("nop"); \
asm("nop"); \
}
