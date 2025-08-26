FROM python:3.13-slim

# Install project dependencies for bcm, gwm and ihu
# Note that pip/setuptools requires the project files (ecus) to be present in the build directory, but we volume mount the later
COPY pyproject.toml README.md LICENSE .
COPY ecus/ ./ecus/
RUN pip install .

CMD ["placeholder_override", "--allow-root"]
