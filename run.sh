#!/usr/bin/env bash
set -euo pipefail

# Authenticate with Remotive Cloud
# remotive cloud auth login

# Mount the recording with transformation
remotive cloud recordings mount 9459066702917749000 \
  --project arm-demo >&2

# Seek to 60 seconds in the recording
# remotive cloud recordings seek 9459066702917749000 \
#   --seconds 60 \
#   --project arm-demo

# Play the recording
remotive cloud recordings playback seek 9459066702917749000 --seconds 0 --project arm-demo  >&2
remotive cloud recordings playback play 9459066702917749000 --project arm-demo  >&2
#remotive cloud recordings playback play 9459066702917749000 --repeat --project arm-demo >&2

echo 'open "https://console.cloud.remotivelabs.com/p/arm-demo/recordings/9459066702917749000?tab=playback"' >&2
echo 'open "https://console.cloud.remotivelabs.com/p/arm-demo/brokers"' >&2

# Print personal broker URL
PERSONAL_URL=$(remotive cloud brokers list --project arm-demo | jq -r '.[] | select(.personal == true) | .url')
echo "$PERSONAL_URL"