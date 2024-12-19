#!/bin/bash
# check-progress.sh

echo "=== Container Status ==="
docker ps -a | grep othor-platform-db-init

echo -e "\n=== Container Logs ==="
docker logs othor-platform-db-init-1

echo -e "\n=== Directory Structure ==="
docker exec othor-platform-db-init-1 ls -R /init-scripts

echo -e "\n=== SQL File Contents ==="
for file in $(docker exec othor-platform-db-init-1 find /init-scripts -name "*.sql"); do
    echo -e "\nFile: $file"
    docker exec othor-platform-db-init-1 cat "$file"
done