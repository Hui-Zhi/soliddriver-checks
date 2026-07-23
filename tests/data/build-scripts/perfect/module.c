/*
 * Perfect KMP Test Module - All Validations Pass
 *
 * This module demonstrates a properly configured KMP that passes
 * all soliddriver-checks validations.
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("SUSE Test Suite");
MODULE_DESCRIPTION("Perfect test module with all validations passing");
MODULE_VERSION("1.0");
MODULE_INFO(supported, "yes");

static int __init perfect_init(void)
{
    printk(KERN_INFO "Perfect test module loaded\n");
    return 0;
}

static void __exit perfect_exit(void)
{
    printk(KERN_INFO "Perfect test module unloaded\n");
}

module_init(perfect_init);
module_exit(perfect_exit);
