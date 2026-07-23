/*
 * No Weak-modules2 Test Module
 *
 * Tests detection of missing weak-modules2 invocation.
 * Module itself is valid but package doesn't invoke WM2.
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("SUSE Test Suite");
MODULE_DESCRIPTION("No weak-modules2 test module");
MODULE_VERSION("1.0");
MODULE_INFO(supported, "yes");

static int __init nowm2_init(void)
{
    printk(KERN_INFO "No WM2 test module loaded\n");
    return 0;
}

static void __exit nowm2_exit(void)
{
    printk(KERN_INFO "No WM2 test module unloaded\n");
}

module_init(nowm2_init);
module_exit(nowm2_exit);
