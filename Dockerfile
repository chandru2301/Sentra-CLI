FROM python:3.10-slim

WORKDIR /scan

# Install sentra
RUN pip install --no-cache-dir sentra

# Set working directory for scans
WORKDIR /scan

ENTRYPOINT ["sentra"]

