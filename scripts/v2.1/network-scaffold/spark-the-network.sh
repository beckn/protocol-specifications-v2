#!/usr/bin/env bash
set -euo pipefail

# ============================================================
#  spark-the-network.sh
#  Minimal org scaffold for rapid network launch
# ============================================================

NETWORK_SLUG="${1:-acmenet}"
WORKDIR="${2:-$PWD/${NETWORK_SLUG}-org-min}"

UPSTREAM_CORE_URL="${UPSTREAM_CORE_URL:-https://github.com/beckn/protocol-specifications.git}"
UPSTREAM_DOMAIN_URL="${UPSTREAM_DOMAIN_URL:-https://github.com/beckn/DEG.git}"

say() { printf "\n\033[1m%s\033[0m\n" "$*"; }

init_repo() {
  local path="$1"
  mkdir -p "$path"
  [ -d "${path}/.git" ] || git -C "$path" init >/dev/null
}

touch_files() {
  local base="$1"; shift
  for f in "$@"; do
    mkdir -p "$(dirname "${base}/${f}")"
    touch "${base}/${f}"
  done
}

add_submodule() {
  local repo_path="$1" sub_url="$2" sub_path="$3"
  if [ -d "${repo_path}/${sub_path}/.git" ] || git -C "$repo_path" config -f .gitmodules --get "submodule.${sub_path}.url" >/dev/null 2>&1; then
    return
  fi
  git -C "$repo_path" submodule add "$sub_url" "$sub_path" >/dev/null
}

REPO_DOTGITHUB=".github"
REPO_PROFILE="${NETWORK_SLUG}-profile"
REPO_SCHEMAS="${NETWORK_SLUG}-schemas"
REPO_EXAMPLES="${NETWORK_SLUG}-examples"
REPO_DOCS="${NETWORK_SLUG}-docs"

P_DOTGITHUB="${WORKDIR}/${REPO_DOTGITHUB}"
P_PROFILE="${WORKDIR}/${REPO_PROFILE}"
P_SCHEMAS="${WORKDIR}/${REPO_SCHEMAS}"
P_EXAMPLES="${WORKDIR}/${REPO_EXAMPLES}"
P_DOCS="${WORKDIR}/${REPO_DOCS}"

say "Creating minimal workspace at: ${WORKDIR}"
mkdir -p "$WORKDIR"

say "Initializing repositories..."
init_repo "$P_DOTGITHUB"
init_repo "$P_PROFILE"
init_repo "$P_SCHEMAS"
init_repo "$P_EXAMPLES"
init_repo "$P_DOCS"

say "Creating placeholder files..."

touch_files "$P_DOTGITHUB" \
  "CONTRIBUTING.md" \
  "SECURITY.md" \
  "PULL_REQUEST_TEMPLATE.md" \
  "workflows/reusable-validate.yml"

touch_files "$P_PROFILE" \
  "README.md" "LICENSE" "NOTICE.md" "CHANGELOG.md" \
  "profile/DEPENDENCIES.yaml" \
  "profile/SUPPORT_MATRIX.md" \
  "profile/CONFORMANCE/discovery.md" \
  "releases/v0.1.0.md"

touch_files "$P_SCHEMAS" \
  "README.md" "LICENSE" "NOTICE.md" "CHANGELOG.md" \
  "context/network/.gitkeep" \
  "jsonschema/network/.gitkeep"

touch_files "$P_EXAMPLES" \
  "README.md" "LICENSE" "NOTICE.md" "CHANGELOG.md" \
  "upstream-refs/ev-charging.yaml" \
  "patches/ev-charging/on_search.patch.json" \
  "generated/ev-charging/on_search.json"

touch_files "$P_DOCS" \
  "README.md" "LICENSE" "NOTICE.md" \
  "mkdocs.yml" \
  "docs/index.md" \
  "docs/ig/ev-charging/overlay.md" \
  "tools/fetch-upstreams/.gitkeep"

say "Adding upstream submodules to docs repo..."
mkdir -p "${P_DOCS}/upstream"
add_submodule "$P_DOCS" "$UPSTREAM_CORE_URL" "upstream/core"
add_submodule "$P_DOCS" "$UPSTREAM_DOMAIN_URL" "upstream/domain"

say "Minimal scaffold complete."
