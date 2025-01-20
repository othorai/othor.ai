#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Docker and Docker Compose
check_docker() {
    if ! command_exists docker; then
        echo "Error: Docker is not installed. Please install Docker first."
        echo "Visit https://docs.docker.com/get-docker/ for installation instructions."
        exit 1
    fi

    if ! command_exists docker-compose; then
        echo "Error: Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit https://docs.docker.com/compose/install/ for installation instructions."
        exit 1
    fi
}

# Function to check if running on Windows and in Git Bash
check_windows_environment() {
    if [[ "$(uname)" == *"MINGW"* ]] || [[ "$(uname)" == *"MSYS"* ]]; then
        if ! command_exists git; then
            echo "Error: Git Bash is required on Windows."
            echo "Please install Git for Windows from https://gitforwindows.org/"
            exit 1
        fi
    fi
}

# Main setup function
main() {
    echo "🚀 Starting Othor.ai setup..."
    
    # Check environment
    check_docker
    check_windows_environment

    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            echo "✅ Created .env file from .env.example"
        else
            echo "❌ Error: .env.example file not found"
            exit 1
        fi
    fi

    # Ensure all shell scripts have LF line endings
    if command_exists dos2unix; then
        find . -type f -name "*.sh" -exec dos2unix {} \;
    fi

    # Start the application
    echo "🏗️  Building and starting services..."
    docker-compose down --remove-orphans
    docker-compose pull
    docker-compose build --no-cache
    docker-compose up -d

    echo "🌟 Setup complete! The application should be running at http://localhost:3000"
    echo "ℹ️  Check docker-compose logs with: docker-compose logs -f"
}

# Run the main function
main