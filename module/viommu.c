#undef pr_fmt
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/kernel.h>
#include <linux/module.h>

static int __init initfunc(void)
{
	return 0;
}
module_init(initfunc);

static void __exit exitfunc(void)
{
	return;
}
module_exit(exitfunc);

MODULE_LICENSE("GPL");
