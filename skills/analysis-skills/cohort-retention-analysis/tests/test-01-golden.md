# Test 01: [Test name]

Type: golden-output | validation-prompt | regression  
Priority: critical | high | medium | low

---

## Purpose

[What this test validates]

---

## Input

```json
{
  "input_1": "test value",
  "input_2": {}
}
```

---

## Golden Output

```json
{
  "output_1": "expected result",
  "output_2": []
}
```

---

## Validation Rules

- [ ] `output_1` matches expected value exactly
- [ ] `output_2` is an array (can be empty)
- [ ] No hallucinated fields present
- [ ] Schema validation passes

---

## Pass/Fail Criteria

**Pass if:** All validation rules are satisfied.  
**Fail if:** Any validation rule fails.

---

## Last run

| Date       | Status | Notes                    |
|------------|--------|--------------------------|
| YYYY-MM-DD | pass   | Initial test             |
