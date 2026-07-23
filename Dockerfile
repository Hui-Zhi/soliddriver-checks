FROM opensuse/tumbleweed:latest

# Install dependencies
RUN zypper --non-interactive install -y \
    python39 \
    python39-pip \
    rpm \
    cpio \
    && zypper clean -a

# Install Python packages
RUN pip3.9 install --no-cache-dir pandas click openpyxl jinja2 bottle lark

# Copy source code
COPY src/ /app/src/
COPY pyproject.toml /app/
COPY setup.py /app/ 2>/dev/null || true

# Install the package
WORKDIR /app
RUN pip3.9 install -e .

# Set entry point
WORKDIR /
ENTRYPOINT ["python3.9", "-m", "soliddriver_checks.cli.cli"]
