FROM opensuse/leap:15.6

WORKDIR /app

# Install dependencies
RUN zypper --non-interactive install -y python39 kmod && \
    zypper --non-interactive clean

# Install pip for Python 3.9
RUN python3.9 -m ensurepip --upgrade || curl https://bootstrap.pypa.io/get-pip.py | python3.9

# Install Python packages
RUN python3.9 -m pip install --no-cache-dir \
    rich \
    pandas \
    setuptools \
    openpyxl \
    click \
    dominate \
    jinja2 \
    bottle \
    requests \
    lark \
    pytest

# Copy the source code
COPY . /app/

# Build and install the package
RUN python3.9 -m pip install -e .

# Create output directory
RUN mkdir -p /output /test-data

WORKDIR /app

# Default command runs tests and shows version
CMD ["sh", "-c", "echo '=== Running Unit Tests ===' && \
     python3.9 -m pytest tests/ -v && \
     echo '' && \
     echo '=== Package Info ===' && \
     soliddriver-checks --version && \
     echo '' && \
     echo '=== Help Output ===' && \
     soliddriver-checks --help"]
