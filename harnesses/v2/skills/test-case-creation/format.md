# Output format

Save test cases to `output/<story_id>.json`:

```json
{
  "story_id": "REF-001",
  "test_cases": [
    {
      "id": "TC-01",
      "title": "Short description of the behaviour under test",
      "type": "positive",
      "preconditions": "State and test data before the test",
      "steps": ["Step 1", "Step 2"],
      "expected": "Observable result"
    }
  ]
}
```

Allowed values for `type`: positive, negative, boundary, security, integration,
data-integrity, audit.
