Run comprehensive validation of the project.

Execute the following commands in sequence and report results:

## 1. Linting

```bash
# Python (ruff):
cd backend && uv run ruff check .

# JavaScript/TypeScript (eslint):
cd frontend && npm run lint
```

**Expected:** No linting errors

## 2. Type Checking (if applicable)

```bash
# Python (mypy):
cd backend && uv run mypy app/

# TypeScript:
cd frontend && npm run typecheck
```

**Expected:** No type errors

## 3. Unit Tests

```bash
# Python (pytest):
cd backend && uv run pytest -v

# JavaScript (vitest/jest):
cd frontend && npm test
```

**Expected:** All tests pass

## 4. Test Coverage

```bash
# Python:
cd backend && uv run pytest --cov=app --cov-report=term-missing

# JavaScript:
cd frontend && npm run test:coverage
```

**Expected:** Coverage meets project threshold

## 5. Build

```bash
cd frontend && npm run build
```

**Expected:** Build completes successfully

## 6. Summary Report

After all validations complete, provide a summary report with:

- Linting status
- Type checking status (if applicable)
- Tests passed/failed
- Coverage percentage
- Build status
- Any errors or warnings encountered
- Overall health assessment (PASS/FAIL)

**Format the report clearly with sections and status indicators**
