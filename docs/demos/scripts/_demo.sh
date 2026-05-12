# Shared helpers for demo scripts.
#
# Source this file from each demo script with:
#     source "$(dirname "$0")/_demo.sh"
#
# Provides:
#   require_env       — fail fast if ANTHROPIC_API_KEY isn't set
#   require_repo_root — ensure we're running from the repo root
#   header "TITLE"    — prints a banner so the cast has visible chapters
#   step "DESC" "CMD" — prints DESC, pauses briefly, runs CMD with a typing
#                       effect so the viewer can read the command first

set -euo pipefail

require_env() {
    if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
        echo "Error: ANTHROPIC_API_KEY is not set. Export it before recording." >&2
        exit 1
    fi
}

require_repo_root() {
    if [ ! -d "agents" ] || [ ! -d "lib" ]; then
        echo "Error: run this script from the repo root." >&2
        exit 1
    fi
}

# Quiet noisy logs unless the user has set their own level.
: "${LOG_LEVEL:=WARNING}"
export LOG_LEVEL

# `header TITLE` — prints a section banner.
header() {
    printf '\n\033[1;34m━━━ %s ━━━\033[0m\n\n' "$1"
    sleep 0.6
}

# `step DESC CMD` — print DESC, fake-type CMD, then run it.
# The fake-typing pause gives a viewer ~1s to read the command before it runs.
step() {
    local desc=$1
    local cmd=$2
    printf '\033[2m# %s\033[0m\n' "$desc"
    sleep 0.5
    printf '\033[1m$ \033[0m'
    # Print one char at a time for a natural typing feel.
    for ((i = 0; i < ${#cmd}; i++)); do
        printf '%s' "${cmd:$i:1}"
        sleep 0.012
    done
    printf '\n'
    sleep 0.2
    eval "$cmd"
    echo
}
