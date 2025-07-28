#!/usr/bin/env bash
set -euo pipefail

# Authenticate with Remotive Cloud
# remotive cloud auth login

# Mount the recording with transformation
remotive cloud recordings mount 13303517729834103000 \
  --project aleks-base-on-open

# Seek to 60 seconds in the recording
# remotive cloud recordings seek 13303517729834103000 \
#   --seconds 60 \
#   --project aleks-base-on-open

# Play the recording
remotive cloud recordings play 13303517729834103000 \
  --project aleks-base-on-open

# Start services via Docker Compose
docker compose \
  -f lighting_and_steering/build/lighting-and-steering/docker-compose.yml \
  --profile jupyter \
  --profile ui up

