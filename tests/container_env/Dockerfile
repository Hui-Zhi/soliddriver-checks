FROM opensuse/leap:15.6

WORKDIR /root

RUN zypper --non-interactive in python311 python311-pip kmod cpio findutils
RUN zypper --non-interactive dup

# easy for rebuild and install, source_codes is created in 
# create_container_***.sh
# install from a copy, so no build files end up in the mounted source tree
RUN echo "rm -rf /tmp/sdc-src && cp -r /root/source_codes /tmp/sdc-src" > build_install.sh
RUN echo "python3.11 -m pip install --force-reinstall /tmp/sdc-src" >> build_install.sh
RUN chmod +x build_install.sh
