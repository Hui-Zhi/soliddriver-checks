// SPDX-License-Identifier: GPL-2.0-only
/*
 * Test kernel module for the soliddriver-checks test suite.
 *
 * It does nothing. Its metadata is set at build time (see Kbuild), so that one
 * source can produce modules with every license, supported flag and PCI alias
 * the checks need to see.
 */
#include <linux/module.h>
#include <linux/pci.h>

static const struct pci_device_id sdc_test_ids[] = {
	{ PCI_DEVICE(SDC_PCI_VENDOR, SDC_PCI_DEVICE) },
	{ }
};
MODULE_DEVICE_TABLE(pci, sdc_test_ids);

static int __init sdc_test_init(void)
{
	pr_info("loaded\n");
	return 0;
}

static void __exit sdc_test_exit(void)
{
}

module_init(sdc_test_init);
module_exit(sdc_test_exit);

MODULE_LICENSE(SDC_LICENSE);
MODULE_DESCRIPTION("soliddriver-checks test module");
#ifdef SDC_SUPPORTED
MODULE_INFO(supported, SDC_SUPPORTED);
#endif
#ifdef SDC_SUPPORTED2
MODULE_INFO(supported, SDC_SUPPORTED2);
#endif
