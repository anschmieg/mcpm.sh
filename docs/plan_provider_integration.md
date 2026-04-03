# MCP Client Manager Re-Evaluation and Local PR Plan

## Repositories evaluated
- https://github.com/pathintegral-institute/mcpm.sh
- https://github.com/gustavodiasdev/mcpx-cli
- Alternative considered for maturity signal: https://github.com/holstein13/mcp-config-manager

## Snapshot (verified 2026-04-02)
| Repository | Approx. commits | Stars | Last push (UTC) |
|---|---:|---:|---|
| `pathintegral-institute/mcpm.sh` | 359 | 917 | 2026-03-27 |
| `gustavodiasdev/mcpx-cli` | 5 | 4 | 2026-02-06 |
| `holstein13/mcp-config-manager` | 127 | 28 | 2026-01-02 |

## Updated decision
**Recommended base: `pathintegral-institute/mcpm.sh`.**

Reason for change:
1. The maintenance/maturity concern is valid: `mcpx-cli` currently has only a handful of commits and low adoption.
2. `mcpm.sh` demonstrates significantly stronger project health (commit cadence, community activity, broader client ecosystem).
3. Your required scope is now better served by extending a mature manager than scaling up an early-stage project.

## How this maps to your requirements
Required clients to ensure support in this PR:
- Mistral Vibe
- Codex
- Claude Code
- Zed Editor
- VSCode
- Crush (Coding Agent)

Optional enhancements in the same PR if straightforward:
- Cherry Studio
- Gemini CLI

`mcpm.sh` already documents client-integration architecture and existing client adapters, so the safest path is to add missing client adapters without changing the core server/profile model.

---

## Draft implementation PR (target: local fork of `mcpm.sh`)

### Proposed PR title
`feat(client): add mistral-vibe, zed, crush, and cherry-studio client adapters`

### Proposed PR body

#### Summary
This PR extends MCPM client integration to support additional MCP clients requested for multi-client workflows.

**Mandatory additions in this PR**
- ✅ Mistral Vibe
- ✅ Zed Editor
- ✅ Crush (Coding Agent)

**Validation of existing required clients**
- ✅ Codex (if already available in target branch, verify read/write + import)
- ✅ Claude Code (verify)
- ✅ VS Code (verify)

**Optional enhancement included**
- ✅ Cherry Studio

#### What changed
1. Added new client adapters under the MCPM client integration layer:
   - `mistral-vibe`
   - `zed`
   - `crush`
   - `cherry-studio`
2. Registered clients in the central client registry for `client ls`, `client edit`, and `client import`.
3. Added/updated path resolvers for each client config location (platform-aware where needed).
4. Implemented config translators for MCPM global server definitions <-> client-native schema.
5. Added fixtures and tests for:
   - adapter write generation
   - import/read normalization
   - round-trip consistency from MCPM model to client config and back
6. Updated docs with a client matrix and per-client caveats.

#### Acceptance criteria
- `mcpm client ls` lists all new adapters.
- `mcpm client edit mistral-vibe|zed|crush|cherry-studio` updates client files correctly.
- `mcpm client import <client>` works for all four new clients.
- Existing client adapters remain backward-compatible.
- Test suite passes with new fixtures.

#### Non-goals
- No redesign of MCPM global config architecture.
- No change to server install/update/profile semantics.

## Execution plan for the local fork PR
1. Fork `pathintegral-institute/mcpm.sh` into your local namespace and clone that fork.
2. Implement adapters in this order: `zed`, `mistral-vibe`, `crush`, `cherry-studio`.
3. Add tests and docs in the same branch.
4. Open a **local (not upstream)** PR from your fork branch.
5. After merge validation, optionally propose upstream contribution.

## Recommendation
Proceed with `mcpm.sh` as the base. This directly addresses the maturity concern while still enabling the requested mandatory and optional client support through additive client-adapter work.
