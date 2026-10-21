---
name: test-case-creation
description: Output format for test cases. Use when writing test cases for a user story.
---
Save test cases to `output/<story_id>.json` in this format:

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

Allowed values for `type`: positive, negative.
