---
name: your-skill-name
description: Brief description of what this skill does (1-2 sentences). Include key triggering words that help agents recognize when to use this skill.
version: 1.0.0
author: Your Name/Team
category: custom
token_estimate: ~500
---

<objective>
[Clear, concise explanation of what problem this skill solves and what capabilities it provides. Keep this to 2-3 sentences maximum.]
</objective>

<when_to_use>
Use this skill when:

- [Specific use case 1 with concrete scenario]
- [Specific use case 2 with concrete scenario]
- [Specific use case 3 with concrete scenario]
- [Additional use cases as needed]

Do NOT use this skill when:

- [Anti-pattern or inappropriate scenario 1]
- [Anti-pattern or inappropriate scenario 2]
</when_to_use>

<prerequisites>
Before using this skill, ensure:

- [Required tool, library, or environment setup]
- [Access to specific resources or credentials]
- [Knowledge prerequisites or dependencies]
- [Other skills that should be loaded alongside this one]

*If there are no prerequisites, remove this section.*
</prerequisites>

<workflow>
<step name="Preparation/Initial Setup">
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
</step>

<step name="Main Process/Core Action">
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
</step>

<step name="Validation/Verification">
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
</step>

<step name="Follow-up/Cleanup">
[Any additional steps needed after main process.]

- Clean up [temporary resources]
- Document [results or decisions]
- Notify [stakeholders or systems]
- Update [tracking or monitoring systems]

*Optional: Remove this step if not applicable.*
</step>
</workflow>

<best_practices>
<practice name="First Best Practice Name">
[Explanation of why this is important and how to apply it.]

**Example:**
```language
// Code demonstrating this best practice
```
</practice>

<practice name="Second Best Practice Name">
[Another key principle with clear guidance.]

**Rationale:** [Why this matters]
**Implementation:** [How to do it]
</practice>

<practice name="Third Best Practice Name">
[Additional recommendation with context.]
</practice>

<practice name="Degree of Freedom">
**[High/Medium/Low]**: [Explanation of how much flexibility agents have]

- **High Freedom**: Multiple valid approaches; adapt based on context and project needs
- **Medium Freedom**: Preferred patterns exist; some variation acceptable for good reasons
- **Low Freedom**: Follow specific procedures exactly; consistency is critical for safety/compliance
</practice>

<practice name="Token Efficiency">
This skill uses approximately **X,XXX tokens** when fully loaded.

**Optimization Strategy:**
- Core instructions: Always loaded (~X,XXX tokens)
- Examples: Load for reference (~XXX tokens)
- Supporting resources: Load on-demand only (variable)
</practice>
</best_practices>

<common_pitfalls>
<pitfall name="Common Mistake">
**What Happens:** [Description of the problem]

**Why It Happens:** [Root cause]

**How to Avoid:**
1. [Prevention step 1]
2. [Prevention step 2]

**Recovery:** [How to fix if it happens]
</pitfall>

<pitfall name="Another Common Issue">
**What Happens:** [Description]

**How to Avoid:** [Prevention strategy]

**Warning Signs:** [Early indicators to watch for]
</pitfall>
</common_pitfalls>

<examples>
<example name="Basic/Common Scenario Name">
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
</example>

<example name="Advanced/Complex Scenario Name">
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
</example>

<example name="Edge Case/Special Scenario Name">
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
</example>
</examples>

<common_patterns>
<pattern name="Pattern Name">
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
</pattern>

<pattern name="Another Pattern Name">
**When to Use:** [Triggering conditions]

**Key Characteristics:**
- [Characteristic 1]
- [Characteristic 2]

**Example:**
```language
// Code demonstrating this pattern
```
</pattern>
</common_patterns>

<troubleshooting>
<issue name="Common Problem">
**Symptoms:** [How to recognize this problem]
- [Observable indicator 1]
- [Observable indicator 2]

**Cause:** [Why this happens]

**Solution:**
1. [First resolution step]
2. [Second resolution step]
3. [Verification step]

**Prevention:** [How to avoid this in future]
</issue>

<issue name="Another Problem">
**Symptoms:** [Observable indicators]

**Diagnostic Steps:**
1. [How to investigate]
2. [What to check]

**Solution:** [Clear resolution steps]

**Alternative Approaches:** [If primary solution doesn't work]
</issue>

<issue name="Third Problem">
**Symptoms:** [How it manifests]

**Quick Fix:** [Immediate solution]

**Root Cause Resolution:** [Permanent fix]
</issue>
</troubleshooting>

<related_skills>
This skill works well with:

- **[Skill Name 1]**: [How these skills complement each other]
- **[Skill Name 2]**: [When to use both together]
- **[Skill Name 3]**: [Integration points]

This skill may conflict with:

- **[Conflicting Skill]**: [Why they shouldn't be used together and when to choose each]
</related_skills>

<integration_notes>
<subsection name="Working with Other Tools">
[How this skill integrates with common tools or workflows]
</subsection>

<subsection name="Skill Composition">
[How to combine this skill with others effectively]
</subsection>

<subsection name="Context Loading Strategy">
**Always Load:**
- [Essential context that should always be present]

**Load When Needed:**
- [Supporting resources to load on-demand]
- [Detailed references for specific scenarios]
</subsection>
</integration_notes>

<notes>
<subsection name="Limitations">
- [Known limitation 1]
- [Known limitation 2]
</subsection>

<subsection name="Future Enhancements">
- [Planned improvement 1]
- [Planned improvement 2]
</subsection>

<subsection name="Assumptions">
- [Assumption about environment or setup]
- [Assumption about user knowledge]
</subsection>
</notes>

<version_history>
**Version 1.0.0 (YYYY-MM-DD)**
- Initial creation
- Core functionality established
- Basic examples provided

**Version 1.1.0 (YYYY-MM-DD)**
- [Enhancement or fix]
- [Additional feature]
</version_history>

<additional_resources>
External documentation and references:

- [Relevant external documentation](https://example.com/docs)
- [Related tool documentation](https://example.com/tools)
- [Team wiki or internal resources](https://internal.example.com/wiki)
</additional_resources>

<template_usage_notes>
**REMOVE THIS SECTION** when creating your actual skill. This guidance is only for template users.

<subsection name="Key Principles">
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
</subsection>

<subsection name="Template Customization">
**Required Sections:**
- objective
- when_to_use
- workflow (with clear steps)
- examples (at least 2)
- best_practices

**Optional Sections** (remove if not applicable):
- prerequisites
- common_pitfalls
- common_patterns
- troubleshooting
- related_skills
- integration_notes
- notes (limitations, assumptions)

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
</subsection>

<subsection name="Testing Checklist">
- [ ] Frontmatter complete and accurate
- [ ] Clear triggering keywords in description
- [ ] Objective section explains "why" not just "what"
- [ ] "When to Use" section has specific scenarios
- [ ] Instructions in imperative form
- [ ] At least 2 concrete, runnable examples
- [ ] Token estimate provided
- [ ] Tested with real agent tasks
- [ ] Agent successfully uses skill when appropriate
- [ ] "Template Usage Notes" section removed
</subsection>

<subsection name="File Organization">
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
</subsection>

<subsection name="Common Mistakes">
- **Too verbose**: Including information agents already have
- **Too vague**: Not providing specific, actionable guidance
- **Missing examples**: Only explaining conceptually
- **Poor triggering**: Description doesn't clearly indicate when to use
- **Resource bloat**: Including everything instead of loading on-demand
- **No testing**: Creating without validating with real agents
</subsection>

<subsection name="Ready to Create Your Skill?">
1. Copy this template: `cp -r skills/custom/template skills/custom/your-skill-name`
2. Update frontmatter with your skill's details
3. Replace template content with your skill's content
4. Add supporting resources if needed
5. Test with target agents
6. Iterate based on usage
7. Remove "Template Usage Notes" section
8. Add to your project's skill catalog

Good luck!
</subsection>
</template_usage_notes>
