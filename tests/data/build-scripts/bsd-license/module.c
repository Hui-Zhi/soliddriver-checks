/*
 * BSD License Test Module
 *
 * Tests BSD license detection (valid open source license).
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

MODULE_LICENSE("Dual BSD/GPL");
MODULE_AUTHOR("SUSE Test Suite");
MODULE_DESCRIPTION("BSD license test module");
MODULE_VERSION("1.0");
MODULE_INFO(supported, "yes");

static int __init bsd_init(void)
{
    printk(KERN_INFO "BSD license test module loaded\n");
    return 0;
}

static void __exit bsd_exit(void)
{
    printk(KERN_INFO "BSD license test module unloaded\n");
}

module_init(bsd_init);
module_exit(bsd_exit);
