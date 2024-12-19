FROM postgres:14-alpine

# Install necessary tools
RUN apk add --no-cache \
    bash \
    curl \
    postgresql-contrib

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

# Set permissions for everything at once
RUN chown -R postgres:postgres /init-scripts /sample-data /var/log/init && \
    chmod -R 755 /init-scripts && \
    chmod -R 644 /sample-data/*.csv && \
    chmod +x /init-scripts/init.sh && \
    chmod -R 777 /var/log/init

# Set the working directory
WORKDIR /init-scripts

# Finally switch to postgres user
USER postgres

CMD ["./init.sh"]