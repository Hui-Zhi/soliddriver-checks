/*
 * Proprietary License Test Module
 * Purpose: Test KMP validation with proprietary license
 */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

MODULE_LICENSE("Proprietary");
MODULE_AUTHOR("SUSE Test");
MODULE_DESCRIPTION("Test module with proprietary license");
MODULE_VERSION("1.0");

static int __init test_init(void)
{
    printk(KERN_INFO "Proprietary test module loaded\n");
    return 0;
}

static void __exit test_exit(void)
{
    printk(KERN_INFO "Proprietary test module unloaded\n");
}

module_init(test_init);
module_exit(test_exit);
