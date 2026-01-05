# Workshop Template

This is a template repository for the Claude Code workshop. It contains the scaffolding and slash commands needed to build a full-stack application with Claude Code.

## What's Included

- **`.claude/commands/`** - Slash commands for planning, execution, validation, and workflow automation
- **`.claude/reference/`** - Best practices documentation for various technologies
- **`CLAUDE.md`** - Template for project-specific instructions (fill this in as you build)

## Getting Started

1. **Fork or clone** this repository
2. **Define your project** — Have a conversation with your AI coding assistant about what you want to build. Discuss requirements, features, and technical decisions.
3. **Create your PRD** — Run `/create-prd` to generate a Product Requirements Document based on your conversation
4. **Build your CLAUDE.md** — Work with the AI assistant to fill in the `CLAUDE.md` template with your project's tech stack, structure, conventions, and commands
5. **Create reference documents** — Add detailed guides to `.claude/reference/` for specific parts of your codebase (e.g., API patterns, database conventions, deployment strategies). Keep your `CLAUDE.md` concise and point to these references when needed — this prevents overwhelming the LLM with context while still giving detailed guidance when working on specific areas.
6. **Start building** — Use the development workflow:
   - `/core_piv_loop:prime` — Load project context
   - `/core_piv_loop:plan-feature` — Create an implementation plan for a feature
   - `/core_piv_loop:execute` — Execute the plan step-by-step

## Claude Commands

Slash commands for Claude Code to assist with development workflows.

### Planning & Execution
| Command | Description |
|---------|-------------|
| `/core_piv_loop:prime` | Load project context and codebase understanding |
| `/core_piv_loop:plan-feature` | Create comprehensive implementation plan with codebase analysis |
| `/core_piv_loop:execute` | Execute an implementation plan step-by-step |

### Validation
| Command | Description |
|---------|-------------|
| `/validation:validate` | Run full validation: tests, linting, coverage, build (customize to your project) |
| `/validation:code-review` | Technical code review on changed files |
| `/validation:code-review-fix` | Fix issues found in code review |
| `/validation:execution-report` | Generate report after implementing a feature |
| `/validation:system-review` | Analyze implementation vs plan for process improvements |

### Bug Fixing
| Command | Description |
|---------|-------------|
| `/github_bug_fix:rca` | Create root cause analysis document for a GitHub issue |
| `/github_bug_fix:implement-fix` | Implement fix based on RCA document |

### Misc
| Command | Description |
|---------|-------------|
| `/commit` | Create atomic commit with appropriate tag (feat, fix, docs, etc.) |
| `/init-project` | Install dependencies and start development servers (customize this to your project) |
| `/create-prd` | Generate Product Requirements Document from conversation |
