# References

This folder contains reference documentation and examples for the ghostwrite-content skill.

## Voice Contract Schema

The skill references the voice contract schema at:
- `templates/voice-contracts/schema.json`

This schema defines the structure for founder voice characteristics including:
- Voice characteristics (tone, vocabulary, sentence structure)
- Signature phrases
- Topics of expertise
- Anti-patterns to avoid
- Example posts for pattern matching

## Related Documentation

### Agents
- [linkedin-topic-curator](../../../agents/workers/linkedin-topic-curator.md) - Topic curation agent
- [linkedin-template-selector](../../../agents/workers/linkedin-template-selector.md) - Template selection agent
- [linkedin-ghostwriter](../../../agents/workers/linkedin-ghostwriter.md) - Content generation agent
- [linkedin-qa-reviewer](../../../agents/workers/linkedin-qa-reviewer.md) - QA review agent

### Templates
- [LinkedIn Post Templates](../../../inputs/_templates/linkedin-post-templates.csv) - 81 LinkedIn post templates

### Schemas
- [Output Schema](../templates/output-schema.json) - Complete skill output schema
- [Post Schema](../templates/post-schema.json) - Individual post schema
- [Calendar Schema](../templates/calendar-schema.json) - Content calendar schema

### Library Modules
- [lib/budget.py](../../../lib/budget.py) - Budget management
- [lib/evaluator.py](../../../lib/evaluator.py) - Quality evaluation
- [lib/runner.py](../../../lib/runner.py) - Workflow execution
- [lib/telemetry.py](../../../lib/telemetry.py) - Cost tracking

## Example Output

See `examples/` folder for sample outputs (when available).
