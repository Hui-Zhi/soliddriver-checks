FROM opensuse/leap:16.1

WORKDIR /root

# python and the tools soliddriver-checks runs
RUN zypper --non-interactive in python313 python313-pip kmod cpio findutils
# for the tests: a kernel to check, tools to build the test KMPs
# (tests/data/build.sh) and pytest
RUN zypper --non-interactive in --no-recommends --force-resolution \
    kernel-default kernel-default-devel rpm-build gcc make openssl gpg2 xz zstd \
    python313-pytest
RUN zypper --non-interactive dup

# the tests that install packages and change /lib/modules only run where this
# is set, see tests/conftest.py
ENV SDC_TEST_CONTAINER=1

# easy for rebuild and install, source_codes is created in
# create_container_***.sh
# install from a copy, so no build files end up in the mounted source tree
RUN echo "rm -rf /tmp/sdc-src && cp -r /root/source_codes /tmp/sdc-src" > build_install.sh
RUN echo "python3.13 -m pip install --force-reinstall /tmp/sdc-src" >> build_install.sh
RUN chmod +x build_install.sh
