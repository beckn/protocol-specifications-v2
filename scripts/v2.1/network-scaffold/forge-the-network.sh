#!/usr/bin/env bash
set -euo pipefail

# ============================================================
#  forge-the-network.sh
#  A repo-forging script for an Open Network GitHub Org layout
# ============================================================

# -----------------------------
# Config (edit these as needed)
# -----------------------------
NETWORK_SLUG="${1:-acmenet}"                      # e.g., acmenet, uei, ondc
WORKDIR="${2:-$PWD/${NETWORK_SLUG}-org}"      # local workspace root

# Upstream repos (replace with real URLs as needed)
UPSTREAM_CORE_URL="${UPSTREAM_CORE_URL:-https://github.com/beckn/protocol-specifications.git}"
UPSTREAM_DOMAIN_URL="${UPSTREAM_DOMAIN_URL:-https://github.com/beckn/DEG.git}"

# Pinned refs (tags/commits/branches). Script does not checkout; it records intent only.
UPSTREAM_CORE_REF="${UPSTREAM_CORE_REF:-v2.0.0}"
UPSTREAM_DOMAIN_REF="${UPSTREAM_DOMAIN_REF:-main}"

# Toggle: create a top-level "workspace" repo to track everything together
CREATE_WORKSPACE_REPO="${CREATE_WORKSPACE_REPO:-true}"

# -----------------------------
# Derived repo names
# -----------------------------
REPO_DOCS="${NETWORK_SLUG}-docs"
REPO_PROFILE="${NETWORK_SLUG}-profile"
REPO_SCHEMAS="${NETWORK_SLUG}-schemas"
REPO_EXAMPLES="${NETWORK_SLUG}-examples"
REPO_TOOLING="${NETWORK_SLUG}-tooling"
REPO_POLICY="${NETWORK_SLUG}-policy"
REPO_DOTGITHUB=".github"

# Local paths
P_DOCS="${WORKDIR}/${REPO_DOCS}"
P_PROFILE="${WORKDIR}/${REPO_PROFILE}"
P_SCHEMAS="${WORKDIR}/${REPO_SCHEMAS}"
P_EXAMPLES="${WORKDIR}/${REPO_EXAMPLES}"
P_TOOLING="${WORKDIR}/${REPO_TOOLING}"
P_POLICY="${WORKDIR}/${REPO_POLICY}"
P_DOTGITHUB="${WORKDIR}/${REPO_DOTGITHUB}"
P_WORKSPACE="${WORKDIR}/${NETWORK_SLUG}-workspace"

# -----------------------------
# Helpers
# -----------------------------
say() { printf "\n\033[1m%s\033[0m\n" "$*"; }

ensure_git() {
  if ! command -v git >/dev/null 2>&1; then
    echo "ERROR: git is not installed or not on PATH."
    exit 1
  fi
}

init_repo() {
  local path="$1"
  local name="$2"
  mkdir -p "$path"
  if [ ! -d "${path}/.git" ]; then
    git -C "$path" init >/dev/null
    touch "${path}/.gitkeep" 2>/dev/null || true
    say "Initialized git repo: ${name}  ->  ${path}"
  else
    say "Repo already initialized: ${name}  ->  ${path}"
  fi
}

touch_files() {
  local base="$1"
  shift
  for f in "$@"; do
    mkdir -p "$(dirname "${base}/${f}")"
    touch "${base}/${f}"
  done
}

add_submodule() {
  local repo_path="$1"
  local sub_url="$2"
  local sub_path="$3"

  if [ -d "${repo_path}/${sub_path}/.git" ] || git -C "$repo_path" config -f .gitmodules --get "submodule.${sub_path}.url" >/dev/null 2>&1; then
    say "Submodule already exists: ${sub_path} in ${repo_path}"
    return
  fi

  git -C "$repo_path" submodule add "$sub_url" "$sub_path" >/dev/null
  say "Added submodule: ${sub_url} -> ${repo_path}/${sub_path}"
}

# -----------------------------
# Main
# -----------------------------
ensure_git

say "Forging org workspace at: ${WORKDIR}"
mkdir -p "$WORKDIR"

say "Creating repos (folders) + initializing git repos..."
init_repo "$P_DOTGITHUB" "$REPO_DOTGITHUB"
init_repo "$P_PROFILE" "$REPO_PROFILE"
init_repo "$P_SCHEMAS" "$REPO_SCHEMAS"
init_repo "$P_EXAMPLES" "$REPO_EXAMPLES"
init_repo "$P_TOOLING" "$REPO_TOOLING"
init_repo "$P_POLICY" "$REPO_POLICY"
init_repo "$P_DOCS" "$REPO_DOCS"

say "Scaffolding file/folder structures..."

# .github
touch_files "$P_DOTGITHUB" \
  "CONTRIBUTING.md" \
  "SECURITY.md" \
  "CODE_OF_CONDUCT.md" \
  "PULL_REQUEST_TEMPLATE.md" \
  "ISSUE_TEMPLATE/bug_report.md" \
  "ISSUE_TEMPLATE/feature_request.md" \
  "workflows/reusable-validate.yml" \
  "workflows/reusable-release.yml"

# profile
touch_files "$P_PROFILE" \
  "README.md" "LICENSE" "NOTICE.md" "CHANGELOG.md" \
  "profile/DEPENDENCIES.yaml" \
  "profile/SUPPORT_MATRIX.md" \
  "profile/POLICY_REFERENCES.md" \
  "profile/CONFORMANCE/discovery.md" \
  "profile/CONFORMANCE/ordering.md" \
  "profile/CONFORMANCE/fulfillment.md" \
  "profile/CONFORMANCE/post_fulfillment.md" \
  "releases/v0.1.0.md"

# schemas
touch_files "$P_SCHEMAS" \
  "README.md" "LICENSE" "NOTICE.md" "CHANGELOG.md" \
  "context/network/.gitkeep" \
  "jsonschema/network/.gitkeep" \
  "mapping/mapping-matrix.csv" \
  "mapping/notes.md"

# examples
touch_files "$P_EXAMPLES" \
  "README.md" "LICENSE" "NOTICE.md" "CHANGELOG.md" \
  "upstream-refs/ev-charging.yaml" \
  "patches/ev-charging/on_search.patch.json" \
  "patches/ev-charging/on_confirm.patch.json" \
  "generated/ev-charging/on_search.json" \
  "generated/ev-charging/on_confirm.json" \
  "reports/latest-validation.json"

# tooling
touch_files "$P_TOOLING" \
  "README.md" "LICENSE" "NOTICE.md" "CHANGELOG.md" \
  "scripts/.gitkeep" \
  "bin/.gitkeep"

# policy
touch_files "$P_POLICY" \
  "README.md" "LICENSE" "NOTICE.md" "CHANGELOG.md" \
  "policies/network-policy.md" \
  "policies/security-policy.md" \
  "policies/onboarding.md"

# docs portal
touch_files "$P_DOCS" \
  "README.md" "LICENSE" "NOTICE.md" \
  "mkdocs.yml" \
  "docs/index.md" \
  "docs/architecture/overview.md" \
  "docs/architecture/participants.md" \
  "docs/architecture/trust-registry.md" \
  "docs/architecture/security.md" \
  "docs/ig/ev-charging/overlay.md" \
  "docs/ig/ev-charging/conformance.md" \
  "docs/ig/ev-charging/workflows/.gitkeep" \
  "docs/ig/ev-charging/faq.md" \
  "docs/schemas/packs.md" \
  "docs/examples/ev-charging.md" \
  "docs/releases/index.md" \
  "tools/fetch-upstreams/.gitkeep"

say "Adding upstream submodules to ${REPO_DOCS}..."
mkdir -p "${P_DOCS}/upstream"
add_submodule "$P_DOCS" "$UPSTREAM_CORE_URL" "upstream/core"
add_submodule "$P_DOCS" "$UPSTREAM_DOMAIN_URL" "upstream/domain"

touch_files "$P_DOCS" "upstream/PINNED_REFS.txt"
cat > "${P_DOCS}/upstream/PINNED_REFS.txt" <<EOF
core_url=${UPSTREAM_CORE_URL}
core_ref=${UPSTREAM_CORE_REF}

domain_url=${UPSTREAM_DOMAIN_URL}
domain_ref=${UPSTREAM_DOMAIN_REF}

NOTE: This file is informational; submodules are not automatically checked out to these refs by this script.
EOF

if [ "${CREATE_WORKSPACE_REPO}" = "true" ]; then
  say "Creating top-level workspace repo (optional)..."
  init_repo "$P_WORKSPACE" "${NETWORK_SLUG}-workspace"

  mkdir -p "${P_WORKSPACE}/repos"
  add_submodule "$P_WORKSPACE" "../${REPO_DOTGITHUB}" "repos/${REPO_DOTGITHUB}"
  add_submodule "$P_WORKSPACE" "../${REPO_PROFILE}"   "repos/${REPO_PROFILE}"
  add_submodule "$P_WORKSPACE" "../${REPO_SCHEMAS}"   "repos/${REPO_SCHEMAS}"
  add_submodule "$P_WORKSPACE" "../${REPO_EXAMPLES}"  "repos/${REPO_EXAMPLES}"
  add_submodule "$P_WORKSPACE" "../${REPO_TOOLING}"   "repos/${REPO_TOOLING}"
  add_submodule "$P_WORKSPACE" "../${REPO_POLICY}"    "repos/${REPO_POLICY}"
  add_submodule "$P_WORKSPACE" "../${REPO_DOCS}"      "repos/${REPO_DOCS}"

  touch_files "$P_WORKSPACE" "README.md" "NOTICE.md"
fi

say "Done."
