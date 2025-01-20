# init-scripts/Dockerfile
FROM postgres:14-alpine

# Install necessary tools including dos2unix for line ending conversion
RUN apk add --no-cache \
    bash \
    curl \
    postgresql-contrib \
    dos2unix

# Stay as root for directory creation and permission setting
USER root

# Create all necessary directories first
RUN mkdir -p /var/log/init \
    /init-scripts/sql \
    /sample-data

# Copy initialization scripts and sample data
COPY sql/*.sql /init-scripts/sql/
COPY init.sh /init-scripts/
COPY sample-data/*.csv /sample-data/

# Convert line endings and set permissions
RUN find /init-scripts -type f \( -name "*.sh" -o -name "*.sql" \) -exec dos2unix {} \; && \
    chown -R postgres:postgres /init-scripts /sample-data /var/log/init && \
    chmod -R 755 /init-scripts && \
    chmod -R 644 /sample-data/*.csv && \
    chmod +x /init-scripts/init.sh && \
    chmod -R 777 /var/log/init

# Set the working directory
WORKDIR /init-scripts

# Finally switch to postgres user
USER postgres

# Ensure script is executed with bash
CMD ["bash", "./init.sh"]