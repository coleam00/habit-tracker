---
description: Analyze and document root cause for a GitHub issue
argument-hint: [github-issue-id]
---

# Root Cause Analysis: GitHub Issue #$ARGUMENTS

## Objective

Investigate GitHub issue #$ARGUMENTS from this repository, identify the root cause, and document findings for future implementation.

**Prerequisites:**
- Working in a local Git repository with GitHub origin
- GitHub CLI installed and authenticated (`gh auth status`)
- Valid GitHub issue ID from this repository

## Investigation Process

### 1. Fetch GitHub Issue Details

**Use GitHub CLI to retrieve issue information:**

```bash
gh issue view $ARGUMENTS
```

This fetches:
- Issue title and description
- Reporter and creation date
- Labels and status
- Comments and discussion

### 2. Search Codebase

**Identify relevant code:**
- Search for components mentioned in issue
- Find related functions, classes, or modules
- Check similar implementations
- Look for patterns or recent changes

Use grep/search to find:
- Error messages from issue
- Related function names
- Component identifiers

### 3. Review Recent History

Check recent changes to affected areas:
!`git log --oneline -20 -- [relevant-paths]`

Look for:
- Recent modifications to affected code
- Related bug fixes
- Refactorings that might have introduced the issue

### 4. Investigate Root Cause

**Analyze the code to determine:**
- What is the actual bug or issue?
- Why is it happening?
- What was the original intent?
- Is this a logic error, edge case, or missing validation?
- Are there related issues or symptoms?

**Consider:**
- Input validation failures
- Edge cases not handled
- Race conditions or timing issues
- Incorrect assumptions
- Missing error handling
- Integration issues between components

### 5. Assess Impact

**Determine:**
- How widespread is this issue?
- What features are affected?
- Are there workarounds?
- What is the severity?
- Could this cause data corruption or security issues?

### 6. Propose Fix Approach

**Design the solution:**
- What needs to be changed?
- Which files will be modified?
- What is the fix strategy?
- Are there alternative approaches?
- What testing is needed?
- Are there any risks or side effects?

## Output: Create RCA Document

Save analysis as: `docs/rca/issue-$ARGUMENTS.md`

### Required RCA Document Structure

```markdown
# Root Cause Analysis: GitHub Issue #$ARGUMENTS

## Issue Summary

- **GitHub Issue ID**: #$ARGUMENTS
- **Issue URL**: [Link to GitHub issue]
- **Title**: [Issue title from GitHub]
- **Reporter**: [GitHub username]
- **Severity**: [Critical/High/Medium/Low]
- **Status**: [Current GitHub issue status]

## Problem Description

[Clear description of the issue]

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Symptoms:**
- [List observable symptoms]

## Reproduction

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Observe issue]

**Reproduction Verified:** [Yes/No]

## Root Cause

### Affected Components

- **Files**: [List of affected files with paths]
- **Functions/Classes**: [Specific code locations]
- **Dependencies**: [Any external deps involved]

### Analysis

[Detailed explanation of the root cause]

**Why This Occurs:**
[Explanation of the underlying issue]

**Code Location:**
```
[File path:line number]
[Relevant code snippet showing the issue]
```

### Related Issues

- [Any related issues or patterns]

## Impact Assessment

**Scope:**
- [How widespread is this?]

**Affected Features:**
- [List affected features]

**Severity Justification:**
[Why this severity level]

**Data/Security Concerns:**
[Any data corruption or security implications]

## Proposed Fix

### Fix Strategy

[High-level approach to fixing]

### Files to Modify

1. **[file-path]**
   - Changes: [What needs to change]
   - Reason: [Why this change fixes it]

2. **[file-path]**
   - Changes: [What needs to change]
   - Reason: [Why this change fixes it]

### Alternative Approaches

[Other possible solutions and why the proposed approach is better]

### Risks and Considerations

- [Any risks with this fix]
- [Side effects to watch for]
- [Breaking changes if any]

### Testing Requirements

**Test Cases Needed:**
1. [Test case 1 - verify fix works]
2. [Test case 2 - verify no regression]
3. [Test case 3 - edge cases]

**Validation Commands:**
```bash
[Exact commands to verify fix]
```

## Implementation Plan

[Brief overview of implementation steps]

This RCA document should be used by `/implement-fix` command.

## Next Steps

1. Review this RCA document
2. Run: `/implement-fix $ARGUMENTS` to implement the fix
3. Run: `/commit` after implementation complete
```
