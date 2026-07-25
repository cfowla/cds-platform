#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

REPO='cfowla/cds-platform'
BASELINE_MAIN='86a14d397b3e0f89e5a1f56f164933d45b76d627'
BRANCH='feature/complete-int2-renal-acceptance'
TEST_LOG="$(mktemp -t int2-renal-pytest.XXXXXX.log)"
PR_BODY="$(mktemp -t int2-renal-pr.XXXXXX.md)"
BOOTSTRAP_LOG="$(mktemp -t int2-renal-bootstrap.XXXXXX.log)"
TEMP_VENV=''
SUCCESS=0

cleanup() {
  rm -f "$PR_BODY"
  [[ -z "$TEMP_VENV" ]] || rm -rf "$TEMP_VENV"
  if [[ "$SUCCESS" -eq 1 ]]; then
    rm -f "$TEST_LOG" "$BOOTSTRAP_LOG"
  else
    printf '\nFocused pytest log retained at: %s\n' "$TEST_LOG" >&2
    if [[ -s "$BOOTSTRAP_LOG" ]]; then
      printf 'Dependency bootstrap log retained at: %s\n' "$BOOTSTRAP_LOG" >&2
    else
      rm -f "$BOOTSTRAP_LOG"
    fi
  fi
}
trap cleanup EXIT

fail() {
  printf '\nERROR: %s\n' "$*" >&2
  exit 1
}

show_dirty_tree() {
  printf 'Working-tree entries:\n' >&2
  while IFS= read -r -d '' entry; do
    printf '  %q\n' "$entry" >&2
  done < <(git status --porcelain=v1 -z)
}

command -v git >/dev/null 2>&1 || fail 'git is unavailable; use a Codespace or repository-connected Codex environment.'
command -v python >/dev/null 2>&1 || fail 'python is unavailable.'

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" \
  || fail 'No complete repository checkout is present. Use a Codespace or repository-connected Codex task.'
cd "$ROOT"

ORIGIN_URL="$(git remote get-url origin 2>/dev/null)" || fail 'The checkout has no origin remote.'
case "$ORIGIN_URL" in
  https://github.com/cfowla/cds-platform|https://github.com/cfowla/cds-platform.git|git@github.com:cfowla/cds-platform.git|ssh://git@github.com/cfowla/cds-platform.git) ;;
  *) fail "Wrong repository origin: $ORIGIN_URL" ;;
esac

if [[ -n "$(git status --porcelain=v1)" ]]; then
  show_dirty_tree
  fail 'Working tree is not clean. Commit, stash, or deliberately remove the listed paths first.'
fi
[[ "$(git config --bool core.sparseCheckout 2>/dev/null || printf false)" != 'true' ]] \
  || fail 'Sparse checkout detected; this is not an acceptable complete checkout.'

missing=0
while IFS= read -r -d '' path; do
  if [[ ! -e "$path" && ! -L "$path" ]]; then
    printf 'Missing tracked path: %s\n' "$path" >&2
    missing=1
  fi
done < <(git ls-files -z)
[[ "$missing" -eq 0 ]] || fail 'The working tree is incomplete.'

required=(
  pyproject.toml
  docs/TASK_TEMPLATE.md
  CURRENT.md
  docs/SAFETY_INVARIANTS.md
  docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md
  src/cds/services/renal.py
  tests/integration/test_renal_dose_matrix.py
  tests/integration/test_renal_safety_invariants.py
)
for path in "${required[@]}"; do
  [[ -f "$path" ]] || fail "Required file is missing: $path"
done

git fetch --prune origin main
REMOTE_MAIN="$(git rev-parse origin/main)"
git merge-base --is-ancestor "$BASELINE_MAIN" "$REMOTE_MAIN" \
  || fail "Reviewed renal-normalization baseline $BASELINE_MAIN is not an ancestor of current main $REMOTE_MAIN."

git switch --detach "$REMOTE_MAIN"
[[ "$(git rev-parse HEAD)" == "$REMOTE_MAIN" ]] || fail 'Could not check out current GitHub main.'
[[ -z "$(git status --porcelain=v1)" ]] || fail 'Checkout became dirty before verification.'

grep -Fq 'crcl = _canonical_plain_decimal(crcl)' src/cds/services/renal.py \
  || fail 'Canonical renal-value normalization is not present on current main.'

SYSTEM_PYTHON="$(command -v python)"
PYTHON_SOURCE='active environment'
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  export PATH="$ROOT/.venv/bin:$PATH"
  PYTHON_SOURCE='repository .venv'
fi

if ! python -m pytest --version >/dev/null 2>&1; then
  printf '\npytest is unavailable; creating an isolated temporary virtual environment.\n'
  TEMP_VENV="$(mktemp -d -t int2-renal-venv.XXXXXX)"
  "$SYSTEM_PYTHON" -m venv "$TEMP_VENV" \
    || fail 'Could not create a temporary virtual environment. Ensure the Python venv module is installed.'
  export PATH="$TEMP_VENV/bin:$PATH"
  PYTHON_SOURCE='temporary isolated venv'

  set +e
  python -m pip install --disable-pip-version-check '.[dev]' \
    2>&1 | tee "$BOOTSTRAP_LOG"
  BOOTSTRAP_STATUS=${PIPESTATUS[0]}
  set -e
  [[ "$BOOTSTRAP_STATUS" -eq 0 ]] \
    || fail 'Could not install project-declared development dependencies from pyproject.toml.'
fi

python -m pytest --version >/dev/null 2>&1 \
  || fail 'pytest remains unavailable after the permitted dependency bootstrap.'
python - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit('Python 3.11 or newer is required by pyproject.toml.')
PY
[[ -z "$(git status --porcelain=v1)" ]] \
  || fail 'Dependency bootstrap changed the tracked or untracked repository state.'

python - <<'PY'
from pathlib import Path
import re

text = Path('tests/integration/test_renal_dose_matrix.py').read_text(encoding='utf-8')
checks = {
    'test_declared_weight_type_conflict_fails_closed strict XFAIL': r'@pytest\.mark\.xfail\(\s*strict=True,.*?\)\s*def test_declared_weight_type_conflict_fails_closed',
    'UNSUP-FAM-WEIGHT strict XFAIL': r'id="UNSUP-FAM-WEIGHT",\s*marks=pytest\.mark\.xfail\(\s*strict=True,',
}
for label, pattern in checks.items():
    if re.search(pattern, text, flags=re.S) is None:
        raise SystemExit(f'Missing required marker: {label}')
PY

printf '\nRunning the exact required acceptance command against %s with %s\n\n' "$REMOTE_MAIN" "$PYTHON_SOURCE"
set +e
python -m pytest -q \
  tests/integration/test_renal_dose_matrix.py \
  tests/integration/test_renal_safety_invariants.py \
  2>&1 | tee "$TEST_LOG"
TEST_STATUS=${PIPESTATUS[0]}
set -e

[[ "$TEST_STATUS" -eq 0 ]] \
  || fail "Focused renal integration gate failed with exit status $TEST_STATUS. No repository files were changed. Log: $TEST_LOG"

PASSED="$(grep -Eo '[0-9]+ passed' "$TEST_LOG" | tail -1 | awk '{print $1}')"
XFAILED="$(grep -Eo '[0-9]+ xfailed' "$TEST_LOG" | tail -1 | awk '{print $1}')"
FAILED="$(grep -Eo '[0-9]+ failed' "$TEST_LOG" | tail -1 | awk '{print $1}' || true)"
XPASSED="$(grep -Eo '[0-9]+ xpassed' "$TEST_LOG" | tail -1 | awk '{print $1}' || true)"
ERRORS="$(grep -Eo '[0-9]+ errors?' "$TEST_LOG" | tail -1 | awk '{print $1}' || true)"
SKIPPED="$(grep -Eo '[0-9]+ skipped' "$TEST_LOG" | tail -1 | awk '{print $1}' || true)"
SUMMARY="$(grep -E '(^|, )[0-9]+ passed' "$TEST_LOG" | tail -1 | sed 's/^[[:space:]]*//')"

[[ "$PASSED" == '117' ]] || fail "Unexpected pass count: ${PASSED:-not found}; expected 117."
[[ "$XFAILED" == '2' ]] || fail "Unexpected XFAIL count: ${XFAILED:-not found}; expected 2."
[[ -z "$FAILED" || "$FAILED" == '0' ]] || fail "Unexpected failures: $FAILED"
[[ -z "$XPASSED" || "$XPASSED" == '0' ]] || fail "Unexpected XPASS results: $XPASSED"
[[ -z "$ERRORS" || "$ERRORS" == '0' ]] || fail "Unexpected errors: $ERRORS"
[[ -z "$SKIPPED" || "$SKIPPED" == '0' ]] || fail "Unexpected skips: $SKIPPED"
[[ -n "$SUMMARY" ]] || fail 'Could not capture the pytest summary line.'
[[ -z "$(git status --porcelain=v1)" ]] || fail 'The focused test run changed the repository working tree.'

command -v gh >/dev/null 2>&1 \
  || fail 'The focused gate passed, but GitHub CLI (gh) is unavailable for the guarded PR and merge steps.'
gh auth status >/dev/null 2>&1 \
  || fail 'The focused gate passed, but gh is not authenticated. Run: gh auth login'
ACTUAL_REPO="$(gh repo view "$REPO" --json nameWithOwner --jq '.nameWithOwner')"
[[ "$ACTUAL_REPO" == "$REPO" ]] || fail "GitHub CLI resolved the wrong repository: $ACTUAL_REPO"

if git show-ref --verify --quiet "refs/heads/$BRANCH" \
  || git show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
  fail "Branch already exists: $BRANCH"
fi

git switch -c "$BRANCH"

export TESTED_SHA="$REMOTE_MAIN"
export PYTEST_SUMMARY="$SUMMARY"
export PYTHON_VERSION="$(python --version 2>&1)"
export PYTEST_VERSION="$(python -m pytest --version | head -1)"
export PYTHON_SOURCE
export VERIFIED_AT="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

python - <<'PY'
from pathlib import Path
import os

tested_sha = os.environ['TESTED_SHA']
summary = os.environ['PYTEST_SUMMARY']
python_version = os.environ['PYTHON_VERSION']
pytest_version = os.environ['PYTEST_VERSION']
python_source = os.environ['PYTHON_SOURCE']
verified_at = os.environ['VERIFIED_AT']

content = f'''# Current Work

This file is replaced after every task. It is not an append-only diary.

## Repository execution mode

Use a complete repository checkout supplied by a Codespace, local development environment, or
repository-connected Codex task. GitHub is authoritative. A repository-local or temporary isolated
virtual environment may be created, and project-declared development dependencies may be installed from
`pyproject.toml`. Do not install dependencies globally or reconstruct an incomplete checkout as
acceptance evidence.

## Roadmap position

- Days 1-82 are complete.
- **Day 83 - Tag the prototype milestone** remains incomplete.
- The original Day 83 candidate `73c3fcfd10548db31c2bf6707e73f65c5e7f2eb0` remains a release
  `no-go`; this focused acceptance result does not certify a new release candidate.
- PR #55 repaired the bounded route and indication integration fixtures.
- PR #58 merged canonical non-exponent renal-value normalization as
  `86a14d397b3e0f89e5a1f56f164933d45b76d627`.
- **INT-2 renal integration acceptance is complete.**

## INT-2 acceptance result

Verified in a complete, clean checkout of `{tested_sha}` at `{verified_at}`.

Environment:

- `{python_version}`
- `{pytest_version}`
- Python source: `{python_source}`

Exact command:

```bash
python -m pytest -q \\
  tests/integration/test_renal_dose_matrix.py \\
  tests/integration/test_renal_safety_invariants.py
```

Exact result:

- `{summary}`
- Exit status: `0`
- The 39 previously failing parameterized `renal_value` textual comparisons now pass.
- Boundary band selection and exact serialized renal-value assertions pass without expectation changes.
- `test_declared_weight_type_conflict_fails_closed` remains strict XFAIL.
- `UNSUP-FAM-WEIGHT` remains strict XFAIL.
- No unrelated failure, error, XPASS, or skip occurred in the two focused files.
- The mismatch was resolved by canonical output normalization already present on `main`; this acceptance
  task changed no implementation, fixture, expected value, safety boundary, public contract, or XFAIL
  marker.

## Remaining repair areas

1. **Work Package 2:** deliberately resolve the renal-content snapshot scope and run only the focused
   snapshot and synthetic-fixture eligibility verification required by the remediation plan.
2. Review the cefepime golden semantic diff before any regeneration.
3. Correct the Decimal-context preservation assertions in the focused renal service tests.
4. Establish and remediate the intended Ruff baseline without repository-wide automatic fixes.
5. Resolve placeholder skips and repair durable release-evidence capture.
6. Select and fully verify a new release candidate only after the preceding work packages are complete.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Validate before calculation or rule matching; unsupported or insufficient cases fail closed.
- Keep identifiers, coding systems, units, and case exact; do not infer, alias, convert, or normalize them.
- Preserve exact Decimal behavior and numeric-string serialization without binary floating-point
  conversion or clinical rounding.
- Preserve public imports, exception behavior, serialization contracts, clinical content, and safety
  boundaries unless a separate task explicitly authorizes a change.
- Do not weaken tests, remove fixtures, overwrite snapshots, regenerate goldens, alter XFAIL markers, or
  modify lint configuration merely to produce a pass.
- Do not create a prototype tag without an explicit `go` decision for one exact unchanged candidate and
  its selected content versions.

## Blockers

- The renal-content snapshot policy is unresolved for synthetic fixtures.
- The cefepime golden semantic difference has not been reviewed.
- Decimal-context tests contain invalid object-equality assertions.
- The intended Ruff ruleset and effective configuration remain unresolved.
- Placeholder-skip dispositions, CLI evidence, clean candidate evidence, independent calculation
  approval, qualified content review, PHI review, release-custodian approval, and a final decision record
  remain incomplete.
- Existing known clinical and architecture limitations remain outside this acceptance task, including
  weight-type conflict handling, the famotidine adult minimum-weight boundary, content supersession,
  standalone CLI composition, and logging-policy wiring.

These blockers still prevent an honest release `go` or prototype milestone tag.

## Files changed

- `CURRENT.md` - records the successful, reproducible INT-2 acceptance result and the next separate work
  package.

No production code, tests, fixtures, content, snapshots, goldens, workflow configuration, or safety
invariant documentation changed.

## Additional files inspected

None beyond the files named by the INT-2 acceptance task and repository/PR metadata needed to verify the
current `main` commit and publish this documentation-only result.

## Next exact action

Use `docs/TASK_TEMPLATE.md` to formulate and execute a separate bounded task for **Work Package 2 —
Resolve the renal-content snapshot scope**. Do not begin that work in the INT-2 pull request.
'''

Path('CURRENT.md').write_text(content, encoding='utf-8')
PY

[[ "$(git diff --name-only)" == 'CURRENT.md' ]] || fail 'A file other than CURRENT.md changed.'
[[ -z "$(git diff --name-only --diff-filter=ACMRTUXB -- '*.py')" ]] || fail 'A Python file changed unexpectedly.'

git diff --check
git diff -- CURRENT.md

git add CURRENT.md
[[ "$(git diff --cached --name-only)" == 'CURRENT.md' ]] || fail 'Staged scope is not exactly CURRENT.md.'
git commit -m 'docs: complete INT-2 renal acceptance'
PR_HEAD="$(git rev-parse HEAD)"
git push --set-upstream origin "$BRANCH"

cat > "$PR_BODY" <<EOF
## Summary

- Records successful INT-2 renal integration acceptance against complete checkout commit \`$TESTED_SHA\`.
- Confirms the 39 prior canonical renal-value text mismatches are resolved.
- Confirms the two existing strict XFAIL cases remain expected failures.
- Identifies Work Package 2 renal snapshot policy as the next separate task.

## Verification

\`\`\`bash
python -m pytest -q \\
  tests/integration/test_renal_dose_matrix.py \\
  tests/integration/test_renal_safety_invariants.py
\`\`\`

Result: \`$PYTEST_SUMMARY\` (exit status 0).

Environment: \`$PYTHON_VERSION\`; \`$PYTEST_VERSION\`; source \`$PYTHON_SOURCE\`.

Strict XFAIL disposition:

- \`test_declared_weight_type_conflict_fails_closed\`
- \`UNSUP-FAM-WEIGHT\`

No failed, errored, skipped, or XPASS test occurred in the focused run.

## Scope

Only \`CURRENT.md\` changed. No production code, test, fixture, expected value, XFAIL marker, content,
snapshot, golden, workflow, or safety documentation changed.
EOF

PR_URL="$(gh pr create \
  --repo "$REPO" \
  --base main \
  --head "$BRANCH" \
  --title 'Complete INT-2 renal integration acceptance' \
  --body-file "$PR_BODY")"
PR_NUMBER="$(gh pr view "$PR_URL" --repo "$REPO" --json number --jq '.number')"

mapfile -t CHANGED_FILES < <(gh api "repos/$REPO/pulls/$PR_NUMBER/files" --paginate --jq '.[].filename')
[[ "${#CHANGED_FILES[@]}" -eq 1 && "${CHANGED_FILES[0]}" == 'CURRENT.md' ]] \
  || fail "PR scope is not exactly CURRENT.md: ${CHANGED_FILES[*]}"

OPEN_HEAD="$(gh pr view "$PR_NUMBER" --repo "$REPO" --json headRefOid --jq '.headRefOid')"
[[ "$OPEN_HEAD" == "$PR_HEAD" ]] || fail 'PR head does not match the committed documentation update.'

CHECK_COUNT="$(gh pr view "$PR_NUMBER" --repo "$REPO" --json statusCheckRollup --jq '.statusCheckRollup | length')"
if [[ "$CHECK_COUNT" -gt 0 ]]; then
  gh pr checks "$PR_NUMBER" --repo "$REPO" --watch --fail-fast
fi

UNRESOLVED_THREADS="$(gh api graphql \
  -f owner='cfowla' \
  -f name='cds-platform' \
  -F number="$PR_NUMBER" \
  -f query='query($owner:String!,$name:String!,$number:Int!){repository(owner:$owner,name:$name){pullRequest(number:$number){reviewThreads(first:100){nodes{isResolved}}}}}' \
  --jq '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)] | length')"
[[ "$UNRESOLVED_THREADS" == '0' ]] || fail "PR has $UNRESOLVED_THREADS unresolved review thread(s)."

REVIEW_DECISION="$(gh pr view "$PR_NUMBER" --repo "$REPO" --json reviewDecision --jq '.reviewDecision // ""')"
[[ "$REVIEW_DECISION" != 'CHANGES_REQUESTED' ]] || fail 'PR has a blocking change request.'
[[ "$REVIEW_DECISION" != 'REVIEW_REQUIRED' ]] || fail 'PR still requires review approval.'

FINAL_HEAD="$(gh pr view "$PR_NUMBER" --repo "$REPO" --json headRefOid --jq '.headRefOid')"
[[ "$FINAL_HEAD" == "$PR_HEAD" ]] || fail 'PR head changed after verification; refusing to merge.'

MERGEABLE='UNKNOWN'
for _ in {1..12}; do
  MERGEABLE="$(gh pr view "$PR_NUMBER" --repo "$REPO" --json mergeable --jq '.mergeable')"
  [[ "$MERGEABLE" == 'UNKNOWN' ]] || break
  sleep 5
done
[[ "$MERGEABLE" == 'MERGEABLE' ]] || fail "PR is not mergeable: $MERGEABLE"

MERGED="$(gh api \
  --method PUT \
  -H 'Accept: application/vnd.github+json' \
  "repos/$REPO/pulls/$PR_NUMBER/merge" \
  -f merge_method='squash' \
  -f sha="$PR_HEAD" \
  -f commit_title='Complete INT-2 renal integration acceptance' \
  --jq '.merged')"
[[ "$MERGED" == 'true' ]] || fail 'GitHub did not merge the pull request.'

SUCCESS=1
printf '\nINT-2 acceptance completed and merged.\nPR: %s\nTest result: %s\n' "$PR_URL" "$PYTEST_SUMMARY"
