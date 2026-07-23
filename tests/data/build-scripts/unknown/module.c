/*
 * Unknown License Test Module
 * Purpose: Test KMP validation with unknown license
 */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

MODULE_LICENSE("Unknown");
MODULE_AUTHOR("ACME Corporation Test Team");
MODULE_DESCRIPTION("Test module with unknown license");
MODULE_VERSION("1.0");

static int __init test_init(void)
{
    printk(KERN_INFO "Unknown license test module loaded\n");
    return 0;
}

static void __exit test_exit(void)
{
    printk(KERN_INFO "Unknown license test module unloaded\n");
}

module_init(test_init);
module_exit(test_exit);
