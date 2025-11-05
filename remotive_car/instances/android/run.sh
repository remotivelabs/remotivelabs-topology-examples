#!/usr/bin/env bash
set -euo pipefail

PROJECT="${1:?Usage: $0 <project> <session_id>}"
SESSION_ID="${2:?Usage: $0 <project> <session_id>}"

# Authenticate with Remotive Cloud
# remotive cloud auth login

# Mount the recording with transformation
remotive cloud recordings mount "$SESSION_ID" \
  --project "$PROJECT" >&2

# Seek to 60 seconds in the recording (optional)
# remotive cloud recordings seek "$SESSION_ID" \
#   --seconds 60 \
#   --project "$PROJECT"

# Play the recording
remotive cloud recordings playback seek "$SESSION_ID" --seconds 0 --project "$PROJECT" >&2
remotive cloud recordings playback play "$SESSION_ID" --project "$PROJECT" >&2
# remotive cloud recordings playback play "$SESSION_ID" --repeat --project "$PROJECT" >&2

echo "open \"https://console.cloud.remotivelabs.com/p/$PROJECT/recordings/$SESSION_ID?tab=playback\"" >&2
echo "open \"https://console.cloud.remotivelabs.com/p/$PROJECT/brokers\"" >&2

# Print personal broker URL
PERSONAL_URL=$(remotive cloud brokers list --project "$PROJECT" | jq -r '.[] | select(.personal == true) | .url')
echo "$PERSONAL_URL"
