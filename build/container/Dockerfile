# hadolint ignore=DL3007
FROM cgr.dev/chainguard/python:latest

# Set the working directory to /home/nonroot
WORKDIR /home/nonroot

# Setup the virtual environment
RUN ["/usr/bin/python3", "-m" , "venv", "--upgrade-deps", ".venv"]
COPY requirements.txt requirements.txt
RUN [".venv/bin/pip", "install", "--disable-pip-version-check", "-r", "requirements.txt"]

# Copy the application
COPY main.py main.py

# Run the application
ENTRYPOINT [".venv/bin/kopf", "run", "-A", "main.py"]
