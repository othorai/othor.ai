#init-scripts/init.sh

#!/bin/bash
# Set safe shell options
set -euo pipefail
IFS=$'\n\t'

# Enable verbose output
if [ "$(uname)" = "Windows_NT" ]; then
    # Handle Windows-specific issues
    export MSYS_NO_PATHCONV=1
    export MSYS2_ARG_CONV_EXCL="*"
fi

# Create log directory with proper error handling
mkdir -p /var/log/init || {
    echo "Failed to create log directory"
    exit 1
}

# Redirect output to log file
exec 1> >(tee -a "/var/log/init/init.log") 2>&1

echo "=== Starting initialization at $(date) ==="

# Verify CSV file exists and is readable
if [ ! -f "/sample-data/wayne_enterprise.csv" ]; then
    echo "Error: CSV file not found at /sample-data/wayne_enterprise.csv"
    ls -la /sample-data/
    exit 1
fi

echo "CSV file found and readable"
echo "First few lines of CSV file:"
head -n 3 /sample-data/wayne_enterprise.csv

# Log environment
echo "Environment:"
echo "POSTGRES_HOST: $POSTGRES_HOST"
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -R /init-scripts

echo "Environment Variables:"
echo "POSTGRES_HOST: $POSTGRES_HOST"
echo "POSTGRES_USER: $POSTGRES_USER"
echo "POSTGRES_DB: $POSTGRES_DB"
PGPASSWORD=$POSTGRES_PASSWORD
echo "POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}"

# Function to run SQL file with proper error handling
run_sql_file() {
    local db=$1
    local file=$2
    
    echo "[$(date)] Attempting database connection:"
    echo "Database: $db"
    echo "User: $POSTGRES_USER"
    echo "Host: $POSTGRES_HOST"
    
    if PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$db" -v ON_ERROR_STOP=1 -f "$file"; then
        echo "[SUCCESS] Executed $file on database $db"
        return 0
    else
        echo "[ERROR] Failed to execute $file on database $db"
        echo "Connection details used:"
        echo "- Host: $POSTGRES_HOST"
        echo "- User: $POSTGRES_USER"
        echo "- Database: $db"
        return 1
    fi
}

# Wait for PostgreSQL to be ready
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -c '\l'; do
    echo "Waiting for PostgreSQL at $POSTGRES_HOST... $(date)"
    sleep 1
done

echo "PostgreSQL is available. Starting initialization..."

# Initialize single database
# Initialize single database
dbname="othor_db"
echo "=== Processing database: $dbname ==="

# Check if database exists more robustly
if PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -lqt | cut -d \| -f 1 | grep -qw "$dbname"; then
    echo "Database $dbname already exists, skipping creation..."
else
    echo "Creating database $dbname..."
    if PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -c "CREATE DATABASE $dbname;" 2>/dev/null; then
        echo "Successfully created database $dbname"
    else
        echo "Failed to create database $dbname, but continuing in case it was created by another process..."
    fi
fi

# Small pause to ensure database is ready
sleep 2

# Run SQL files in order
for sqlfile in /init-scripts/sql/0{1,2,3,4,5}-*.sql; do
    if [ -f "$sqlfile" ]; then
        echo "Processing $sqlfile..."
        if ! run_sql_file "$dbname" "$sqlfile"; then
            echo "Error processing $sqlfile for $dbname"
            exit 1
        fi
    else
        echo "Warning: SQL file pattern $sqlfile not found"
    fi
done

echo "Completed processing database: $dbname"

echo "=== Database initialization completed at $(date) ==="

# Function to get authentication token
get_auth_token() {
    local max_retries=5
    local retry_count=0
    local wait_time=10

    while [ $retry_count -lt $max_retries ]; do
        echo "Getting authentication token (attempt $((retry_count + 1))/$max_retries)..." >&2

        local auth_response=$(curl -s -X POST http://auth:8000/authorization/login \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -d "username=admin@example.com" \
            -d "password=admin123")

        if [ $? -eq 0 ] && [ ! -z "$auth_response" ]; then
            # Extract only the token
            local token=$(echo $auth_response | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
            if [ ! -z "$token" ]; then
                # Return only the token, without any logging text
                echo "$token"
                return 0
            fi
        fi
        
        echo "Failed to get token, waiting ${wait_time}s before retry..." >&2
        sleep $wait_time
        retry_count=$((retry_count + 1))
    done
    
    echo "Failed to get authentication token after $max_retries attempts" >&2
    return 1
}

# Wait for backend-auth service to be available
echo "Waiting for backend-auth service..."
max_retries=30
retry_count=0

while ! curl -s http://auth:8000/health > /dev/null && [ $retry_count -lt $max_retries ]; do
    echo "Backend auth service unavailable - attempt $((retry_count + 1))/$max_retries"
    sleep 5
    retry_count=$((retry_count + 1))
done

if [ $retry_count -eq $max_retries ]; then
    echo "Failed to connect to backend-auth service after $max_retries attempts"
    exit 1
fi

# Get authentication token
token=$(get_auth_token)
if [ $? -ne 0 ]; then
    echo "Failed to get authentication token"
    exit 1
fi

metric_discovery_request() {
    local token="$1"
    local max_retries=5
    local retry_count=0
    local wait_time=10

    while [ $retry_count -lt $max_retries ]; do
        echo "Making metric discovery request (attempt $((retry_count + 1))/$max_retries)..."
        
        local response=$(curl -s -X POST \
            "http://auth:8000/metric-discovery/metrics/discover/e89be664-c83d-4661-9e52-a654c0a45d6c" \
            -H "Authorization: Bearer ${token}" \
            -H "Content-Type: application/json")

        echo "Metric discovery response: $response"
        
        # If response doesn't contain error indicators, consider it successful
        if ! echo "$response" | grep -q "error\|failed\|detail\|Invalid"; then
            return 0
        fi
        
        echo "Attempt $((retry_count + 1)) failed, waiting ${wait_time}s before retry..."
        sleep $wait_time
        retry_count=$((retry_count + 1))
    done
    
    echo "Metric discovery failed after $max_retries attempts. Last response: $response"
    return 1
}

# Replace the existing metric discovery section with:
echo "Making metric discovery request with token..."
if ! metric_discovery_request "$token"; then
    echo "Metric discovery request failed"
    exit 1
fi

echo "Metric discovery response: $response"

# Check if the response indicates success
if echo "$response" | grep -q "error\|failed\|detail"; then
    echo "Metric discovery failed with response: $response"
    exit 1
fi

echo "=== Initialization process complete! ==="