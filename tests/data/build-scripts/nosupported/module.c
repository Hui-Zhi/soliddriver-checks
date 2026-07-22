/*
 * No Supported Flag Test Module
 * Purpose: Test KMP validation with GPL license but no MODULE_INFO(supported)
 */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("SUSE Test");
MODULE_DESCRIPTION("Test module with GPL but no supported flag");
MODULE_VERSION("1.0");
/* Intentionally missing: MODULE_INFO(supported, "yes") or MODULE_INFO(supported, "external") */

static int __init test_init(void)
{
    printk(KERN_INFO "No-supported test module loaded\n");
    return 0;
}

static void __exit test_exit(void)
{
    printk(KERN_INFO "No-supported test module unloaded\n");
}

module_init(test_init);
module_exit(test_exit);
