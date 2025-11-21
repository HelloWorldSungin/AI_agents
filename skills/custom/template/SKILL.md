---
name: your-skill-name
description: Brief description of what this skill does (1-2 sentences). Include key triggering words that help agents recognize when to use this skill.
version: 1.0.0
author: Your Name/Team
category: custom
token_estimate: ~500
---

# [Skill Name] Skill

## Purpose

[Clear, concise explanation of what problem this skill solves and what capabilities it provides. Keep this to 2-3 sentences maximum.]

## When to Use This Skill

Use this skill when:

- [Specific use case 1 with concrete scenario]
- [Specific use case 2 with concrete scenario]
- [Specific use case 3 with concrete scenario]
- [Additional use cases as needed]

Do NOT use this skill when:

- [Anti-pattern or inappropriate scenario 1]
- [Anti-pattern or inappropriate scenario 2]

## Prerequisites

Before using this skill, ensure:

- [Required tool, library, or environment setup]
- [Access to specific resources or credentials]
- [Knowledge prerequisites or dependencies]
- [Other skills that should be loaded alongside this one]

*If there are no prerequisites, remove this section.*

## Instructions

### Step 1: [Preparation/Initial Setup]

[Detailed instructions for the first step. Use imperative form (commands).]

- Check that [prerequisite] is available
- Verify [condition] is met
- Gather [required information]

**Example:**
```bash
# Command to verify setup
tool --version

# Command to check prerequisites
tool check --all
```

### Step 2: [Main Process/Core Action]

[Instructions for the primary workflow.]

1. Execute [specific action]
2. Monitor [specific indicator]
3. Validate [expected condition]

**Important Considerations:**
- [Key decision point or branching logic]
- [Edge case to handle]
- [Safety check or validation]

**Example:**
```python
# Example code showing this step
def main_process():
    """Core implementation of the skill's main action."""
    # Step-by-step implementation
    result = perform_action()
    validate(result)
    return result
```

### Step 3: [Validation/Verification]

[Instructions for confirming success.]

Verify the process completed successfully by:

1. Checking [specific output or indicator]
2. Confirming [expected state or condition]
3. Running [validation command or test]

**Expected Outcomes:**
- [Specific success criterion 1]
- [Specific success criterion 2]

**Example:**
```bash
# Validation commands
tool verify --output
tool status --check-all
```

### Step 4: [Follow-up/Cleanup] (Optional)

[Any additional steps needed after main process.]

- Clean up [temporary resources]
- Document [results or decisions]
- Notify [stakeholders or systems]
- Update [tracking or monitoring systems]

## Best Practices

### 1. [First Best Practice Name]

[Explanation of why this is important and how to apply it.]

**Example:**
```language
// Code demonstrating this best practice
```

### 2. [Second Best Practice Name]

[Another key principle with clear guidance.]

**Rationale:** [Why this matters]
**Implementation:** [How to do it]

### 3. [Third Best Practice Name]

[Additional recommendation with context.]

### 4. Degree of Freedom

**[High/Medium/Low]**: [Explanation of how much flexibility agents have]

- **High Freedom**: Multiple valid approaches; adapt based on context and project needs
- **Medium Freedom**: Preferred patterns exist; some variation acceptable for good reasons
- **Low Freedom**: Follow specific procedures exactly; consistency is critical for safety/compliance

### 5. Token Efficiency

This skill uses approximately **X,XXX tokens** when fully loaded.

**Optimization Strategy:**
- Core instructions: Always loaded (~X,XXX tokens)
- Examples: Load for reference (~XXX tokens)
- Supporting resources: Load on-demand only (variable)

## Common Pitfalls

### Pitfall 1: [Common Mistake]

**What Happens:** [Description of the problem]

**Why It Happens:** [Root cause]

**How to Avoid:**
1. [Prevention step 1]
2. [Prevention step 2]

**Recovery:** [How to fix if it happens]

### Pitfall 2: [Another Common Issue]

**What Happens:** [Description]

**How to Avoid:** [Prevention strategy]

**Warning Signs:** [Early indicators to watch for]

## Examples

### Example 1: [Basic/Common Scenario Name]

**Context:** [When you'd use this approach]

**Situation:** [Specific setup or starting conditions]

**Steps:**
1. [First action taken]
2. [Second action taken]
3. [Third action taken]

**Implementation:**
```language
# Complete, runnable example
def example_basic():
    """Demonstrate basic usage of this skill."""
    # Step 1: Setup
    config = load_config()

    # Step 2: Execute
    result = execute_action(config)

    # Step 3: Validate
    assert verify(result), "Validation failed"

    return result
```

**Expected Output:**
```
[Sample output showing what success looks like]
```

**Outcome:** [What was accomplished and why it matters]

---

### Example 2: [Advanced/Complex Scenario Name]

**Context:** [More sophisticated use case]

**Situation:** [Specific setup with additional complexity]

**Challenges:**
- [Challenge or constraint 1]
- [Challenge or constraint 2]

**Steps:**
1. [First action with additional considerations]
2. [Second action handling edge cases]
3. [Third action with error handling]

**Implementation:**
```language
# More sophisticated example
class AdvancedExample:
    """Demonstrate advanced usage with error handling."""

    def __init__(self, config):
        self.config = config
        self.state = {}

    def execute(self):
        """Main execution with comprehensive error handling."""
        try:
            # Step 1: Preparation
            self._prepare()

            # Step 2: Core process
            result = self._process()

            # Step 3: Validation
            self._validate(result)

            return result

        except SpecificError as e:
            # Handle known error
            self._handle_error(e)

        except Exception as e:
            # Handle unexpected error
            self._handle_unexpected_error(e)

    def _prepare(self):
        """Preparation logic."""
        pass

    def _process(self):
        """Core processing logic."""
        pass

    def _validate(self, result):
        """Validation logic."""
        pass
```

**Expected Output:**
```
[Sample output for advanced scenario]
```

**Outcome:** [What was accomplished, including handling of complexity]

---

### Example 3: [Edge Case/Special Scenario Name]

**Context:** [Unusual but important situation]

**Special Considerations:**
- [Unique aspect 1]
- [Unique aspect 2]

**Implementation:**
```language
# Example handling edge case
def handle_edge_case():
    """Demonstrate how to handle special scenarios."""
    # Implementation details
    pass
```

**Outcome:** [Result and lessons learned]

## Common Patterns

### Pattern 1: [Pattern Name]

**When to Use:** [Triggering conditions for this pattern]

**Approach:**
1. [Step 1 of pattern]
2. [Step 2 of pattern]
3. [Step 3 of pattern]

**Example:**
```language
// Code demonstrating this pattern
def pattern_one():
    """Implementation of common pattern 1."""
    pass
```

### Pattern 2: [Another Pattern Name]

**When to Use:** [Triggering conditions]

**Key Characteristics:**
- [Characteristic 1]
- [Characteristic 2]

**Example:**
```language
// Code demonstrating this pattern
```

## Troubleshooting

### Issue 1: [Common Problem]

**Symptoms:** [How to recognize this problem]
- [Observable indicator 1]
- [Observable indicator 2]

**Cause:** [Why this happens]

**Solution:**
1. [First resolution step]
2. [Second resolution step]
3. [Verification step]

**Prevention:** [How to avoid this in future]

### Issue 2: [Another Problem]

**Symptoms:** [Observable indicators]

**Diagnostic Steps:**
1. [How to investigate]
2. [What to check]

**Solution:** [Clear resolution steps]

**Alternative Approaches:** [If primary solution doesn't work]

### Issue 3: [Third Problem]

**Symptoms:** [How it manifests]

**Quick Fix:** [Immediate solution]

**Root Cause Resolution:** [Permanent fix]

## Related Skills

This skill works well with:

- **[Skill Name 1]**: [How these skills complement each other]
- **[Skill Name 2]**: [When to use both together]
- **[Skill Name 3]**: [Integration points]

This skill may conflict with:

- **[Conflicting Skill]**: [Why they shouldn't be used together and when to choose each]

## Integration Notes

### Working with Other Tools

[How this skill integrates with common tools or workflows]

### Skill Composition

[How to combine this skill with others effectively]

### Context Loading Strategy

**Always Load:**
- [Essential context that should always be present]

**Load When Needed:**
- [Supporting resources to load on-demand]
- [Detailed references for specific scenarios]

## Notes

### Limitations

- [Known limitation 1]
- [Known limitation 2]

### Future Enhancements

- [Planned improvement 1]
- [Planned improvement 2]

### Assumptions

- [Assumption about environment or setup]
- [Assumption about user knowledge]

## Version History

### Version 1.0.0 (YYYY-MM-DD)
- Initial creation
- Core functionality established
- Basic examples provided

### Version 1.1.0 (YYYY-MM-DD)
- [Enhancement or fix]
- [Additional feature]

## Additional Resources

External documentation and references:

- [Relevant external documentation](https://example.com/docs)
- [Related tool documentation](https://example.com/tools)
- [Team wiki or internal resources](https://internal.example.com/wiki)

---

## Notes for Skill Creators

**REMOVE THIS SECTION** when creating your actual skill. This guidance is only for template users.

### Key Principles

1. **Concise and Actionable**: Every sentence should provide value. Remove fluff.

2. **Imperative Form**: Write as commands ("Do this", "Check that") not descriptions.

3. **Progressive Disclosure**:
   - Frontmatter metadata: ~50-100 tokens (always in context)
   - SKILL.md body: 2,000-5,000 tokens (loaded when skill triggered)
   - Supporting resources: Variable (loaded on-demand)

4. **Concrete Examples**: One good example > 10 paragraphs of explanation.

5. **Appropriate Specificity**:
   - **High freedom**: Provide principles, options, and trade-offs
   - **Medium freedom**: Show preferred patterns with acceptable alternatives
   - **Low freedom**: Give exact procedures with safety checks

6. **Test with Real Tasks**: Validate effectiveness with actual agent workflows.

### Template Customization

**Required Sections:**
- Purpose
- When to Use This Skill
- Instructions (with clear steps)
- Examples (at least 2)
- Best Practices

**Optional Sections** (remove if not applicable):
- Prerequisites
- Common Pitfalls
- Common Patterns
- Troubleshooting
- Related Skills
- Integration Notes
- Notes (limitations, assumptions)

**Customize Based on Skill Type:**

**For Workflow/Process Skills:**
- Emphasize step-by-step instructions
- Include decision trees for branching logic
- Provide checklist format options
- Document approval/review steps

**For Technical/Implementation Skills:**
- Focus on code examples
- Include architecture patterns
- Document API usage
- Provide testing strategies

**For Domain/Knowledge Skills:**
- Emphasize concepts and principles
- Include reference materials
- Document domain-specific patterns
- Provide terminology glossary

### Testing Checklist

- [ ] Frontmatter complete and accurate
- [ ] Clear triggering keywords in description
- [ ] Purpose section explains "why" not just "what"
- [ ] "When to Use" section has specific scenarios
- [ ] Instructions in imperative form
- [ ] At least 2 concrete, runnable examples
- [ ] Token estimate provided
- [ ] Tested with real agent tasks
- [ ] Agent successfully uses skill when appropriate
- [ ] "Notes for Skill Creators" section removed

### File Organization

```
your-skill-name/
├── SKILL.md              # This file (required)
├── scripts/              # Executable scripts (optional)
│   ├── helper.py
│   └── utility.sh
├── references/           # Documentation (optional)
│   ├── api_reference.md
│   └── detailed_guide.md
└── assets/              # Templates, configs (optional)
    ├── template.json
    └── example_output.txt
```

### Common Mistakes

- **Too verbose**: Including information agents already have
- **Too vague**: Not providing specific, actionable guidance
- **Missing examples**: Only explaining conceptually
- **Poor triggering**: Description doesn't clearly indicate when to use
- **Resource bloat**: Including everything instead of loading on-demand
- **No testing**: Creating without validating with real agents

---

**Ready to create your skill?**

1. Copy this template: `cp -r skills/custom/template skills/custom/your-skill-name`
2. Update frontmatter with your skill's details
3. Replace template content with your skill's content
4. Add supporting resources if needed
5. Test with target agents
6. Iterate based on usage
7. Remove "Notes for Skill Creators" section
8. Add to your project's skill catalog

Good luck!
