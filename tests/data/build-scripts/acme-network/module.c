/*
 * ACME Corporation Network Driver
 * Purpose: Test module that passes all validations
 */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("ACME Corporation");
MODULE_DESCRIPTION("ACME Network Adapter Driver");
MODULE_VERSION("1.0.0");
MODULE_INFO(supported, "external");

static int __init acme_init(void)
{
    printk(KERN_INFO "ACME network driver loaded\n");
    return 0;
}

static void __exit acme_exit(void)
{
    printk(KERN_INFO "ACME network driver unloaded\n");
}

module_init(acme_init);
module_exit(acme_exit);
