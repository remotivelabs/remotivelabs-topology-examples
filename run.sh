#!/usr/bin/env bash
set -euo pipefail

# Authenticate with Remotive Cloud
# remotive cloud auth login



# Mount the recording with transformation
remotive cloud recordings mount 9459066702917749000 \
  --project arm-demo

# Seek to 60 seconds in the recording
# remotive cloud recordings seek 9459066702917749000 \
#   --seconds 60 \
#   --project arm-demo

# Play the recording
remotive cloud recordings playback play 9459066702917749000 --project arm-demo
#remotive cloud recordings playback play 9459066702917749000 --repeat --project arm-demo

echo 'open "https://console.cloud.remotivelabs.com/p/arm-demo/recordings/9459066702917749000?tab=playback"'
echo 'open "https://console.cloud.remotivelabs.com/p/arm-demo/brokers"'

# Start services via Docker Compose
docker compose \
  -f lighting_and_steering/build/lighting-and-steering/docker-compose.yml \
  --profile jupyter \
  --profile ui up

