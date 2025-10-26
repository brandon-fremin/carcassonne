#!/usr/bin/env bash
# Usage:
#   source ./load_env.sh .env
# or:
#   cat .env | source ./load_env.sh

set -euo pipefail

input="${1:-/dev/stdin}"

while IFS='=' read -r key value; do
    # Skip comments and empty lines
    [[ -z "$key" || "$key" =~ ^# ]] && continue

    # Trim whitespace
    key="$(echo "$key" | xargs)"
    value="$(echo "$value" | xargs)"

    # Skip invalid keys (no name before =)
    [[ -z "$key" ]] && continue

    # Remove surrounding quotes if any
    value="${value%\"}"
    value="${value#\"}"
    value="${value%\'}"
    value="${value#\'}"

    # Export safely
    export "$key=$value"
    echo "Exported: $key=$value"
done < "$input"