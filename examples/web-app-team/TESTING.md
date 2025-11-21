# Testing Web App Team Configuration

This guide shows how to test the web-app-team configuration with skills integration.

## Prerequisites

```bash
# Ensure AI Agents library is installed
cd /path/to/AI_agents

# Verify skills directory exists
ls -la skills/

# Expected output:
# skills/core/
# skills/communication/
# skills/design/
# skills/documents/
```

## Test 1: Compose Individual Agents

### Frontend Developer with Skills

```bash
python scripts/compose-agent.py \
  --config examples/web-app-team/config.yml \
  --agent frontend_developer \
  --output /tmp/frontend-dev-composed.md
```

**Expected Output**:
```
Loading configuration from examples/web-app-team/config.yml
Composing agent: frontend_developer
  ✓ Loaded base: base/software-developer.md
  ✓ Loaded platform: platforms/web/frontend-developer.md
  ✓ Loaded skill: core/web-artifacts-builder
  ✓ Loaded skill: core/webapp-testing
  ✓ Loaded skill: design/theme-factory
  ✓ Wrote composed prompt to /tmp/frontend-dev-composed.md

Token estimate: ~13,000 tokens
```

**Verification**:
```bash
# Check that skills were included
grep -c "web-artifacts-builder" /tmp/frontend-dev-composed.md  # Should be > 0
grep -c "webapp-testing" /tmp/frontend-dev-composed.md         # Should be > 0
grep -c "theme-factory" /tmp/frontend-dev-composed.md          # Should be > 0

# Check file size (should be substantial)
wc -l /tmp/frontend-dev-composed.md  # Should be 300+ lines
```

### Backend Developer with Skills

```bash
python scripts/compose-agent.py \
  --config examples/web-app-team/config.yml \
  --agent backend_developer \
  --output /tmp/backend-dev-composed.md
```

**Expected Output**:
```
Loading configuration from examples/web-app-team/config.yml
Composing agent: backend_developer
  ✓ Loaded base: base/software-developer.md
  ✓ Loaded platform: platforms/web/backend-developer.md
  ✓ Loaded skill: core/mcp-builder
  ✓ Loaded skill: core/webapp-testing
  ✓ Loaded skill: documents/xlsx
  ✓ Wrote composed prompt to /tmp/backend-dev-composed.md

Token estimate: ~12,000 tokens
```

**Verification**:
```bash
grep -c "mcp-builder" /tmp/backend-dev-composed.md    # Should be > 0
grep -c "MCP server" /tmp/backend-dev-composed.md     # Should be > 0
grep -c "FastMCP\|TypeScript" /tmp/backend-dev-composed.md  # Should be > 0
```

### QA Tester with Skills

```bash
python scripts/compose-agent.py \
  --config examples/web-app-team/config.yml \
  --agent qa_tester \
  --output /tmp/qa-tester-composed.md
```

**Expected Output**:
```
Loading configuration from examples/web-app-team/config.yml
Composing agent: qa_tester
  ✓ Loaded base: base/qa-tester.md
  ✓ Loaded skill: core/webapp-testing
  ✓ Loaded skill: documents/xlsx
  ✓ Loaded skill: documents/pdf
  ✓ Wrote composed prompt to /tmp/qa-tester-composed.md

Token estimate: ~11,000 tokens
```

**Verification**:
```bash
grep -c "Playwright" /tmp/qa-tester-composed.md  # Should be > 0
grep -c "xlsx" /tmp/qa-tester-composed.md        # Should be > 0
grep -c "pdf" /tmp/qa-tester-composed.md         # Should be > 0
```

### Team Manager with Skills

```bash
python scripts/compose-agent.py \
  --config examples/web-app-team/config.yml \
  --agent team_manager \
  --output /tmp/team-manager-composed.md
```

**Expected Output**:
```
Loading configuration from examples/web-app-team/config.yml
Composing agent: team_manager
  ✓ Loaded base: base/manager.md
  ✓ Loaded skill: communication/internal-comms
  ✓ Loaded skill: documents/pptx
  ✓ Loaded skill: core/skill-creator
  ✓ Wrote composed prompt to /tmp/team-manager-composed.md

Token estimate: ~11,000 tokens
```

**Verification**:
```bash
grep -c "3P update" /tmp/team-manager-composed.md       # Should be > 0
grep -c "internal-comms" /tmp/team-manager-composed.md  # Should be > 0
grep -c "pptx" /tmp/team-manager-composed.md           # Should be > 0
```

## Test 2: Compose All Agents

```bash
# Compose all agents at once
for agent in team_manager frontend_developer backend_developer qa_tester; do
  echo "Composing $agent..."
  python scripts/compose-agent.py \
    --config examples/web-app-team/config.yml \
    --agent $agent \
    --output /tmp/$agent-composed.md
done
```

**Expected Outcome**: All 4 agents successfully composed with skills

## Test 3: Token Budget Analysis

```bash
# Count tokens for each agent (approximate using word count)
for agent in team_manager frontend_developer backend_developer qa_tester; do
  file="/tmp/$agent-composed.md"
  words=$(wc -w < "$file")
  # Rough estimate: 1 token ≈ 0.75 words for English
  tokens=$((words * 4 / 3))
  echo "$agent: ~$tokens tokens ($words words)"
done
```

**Expected Output** (approximate):
```
team_manager: ~11,000 tokens (8,250 words)
frontend_developer: ~13,000 tokens (9,750 words)
backend_developer: ~12,000 tokens (9,000 words)
qa_tester: ~11,000 tokens (8,250 words)
```

**Total Team Budget**: ~47,000 tokens

## Test 4: Skill Content Verification

### Verify web-artifacts-builder in Frontend Developer

```bash
# Extract skill section
sed -n '/## Skill: web-artifacts-builder/,/## End Skill/p' \
  /tmp/frontend-dev-composed.md | head -50
```

**Expected Content**:
- React component creation guidance
- Tailwind CSS usage
- shadcn/ui component library
- Interactive artifact patterns

### Verify mcp-builder in Backend Developer

```bash
# Extract skill section
sed -n '/## Skill: mcp-builder/,/## End Skill/p' \
  /tmp/backend-dev-composed.md | head -50
```

**Expected Content**:
- MCP server architecture
- FastMCP and TypeScript SDK references
- Tool schema design
- API integration patterns

### Verify internal-comms in Team Manager

```bash
# Extract skill section
sed -n '/## Skill: internal-comms/,/## End Skill/p' \
  /tmp/team-manager-composed.md | head -50
```

**Expected Content**:
- 3P update format (Progress/Plans/Problems)
- Company newsletter templates
- FAQ response guidelines
- Status report structures

## Test 5: Error Handling

### Test with Missing Skill

Create a test config with a non-existent skill:

```bash
cat > /tmp/test-config.yml << 'EOF'
agents:
  test_agent:
    base: "base/software-developer.md"
    skills:
      - "core/web-artifacts-builder"
      - "nonexistent/fake-skill"  # This doesn't exist
      - "documents/pdf"
EOF

python scripts/compose-agent.py \
  --config /tmp/test-config.yml \
  --agent test_agent \
  --output /tmp/test-output.md
```

**Expected Behavior**:
- Warning message about missing skill
- Graceful fallback (skip the missing skill)
- Other skills still loaded
- Process completes successfully

**Expected Output**:
```
Loading configuration from /tmp/test-config.yml
Composing agent: test_agent
  ✓ Loaded base: base/software-developer.md
  ✓ Loaded skill: core/web-artifacts-builder
  ⚠ Warning: Skill not found: nonexistent/fake-skill
  ✓ Loaded skill: documents/pdf
  ✓ Wrote composed prompt to /tmp/test-output.md

Token estimate: ~9,000 tokens
```

## Test 6: Skill Deduplication

Test that skills are not loaded twice if specified multiple times:

```bash
cat > /tmp/duplicate-config.yml << 'EOF'
agents:
  test_agent:
    base: "base/software-developer.md"
    skills:
      - "core/web-artifacts-builder"
      - "core/web-artifacts-builder"  # Duplicate
      - "documents/pdf"
EOF

python scripts/compose-agent.py \
  --config /tmp/duplicate-config.yml \
  --agent test_agent \
  --output /tmp/test-dedup.md
```

**Expected Behavior**:
- Skill loaded only once
- No duplicate content in output
- Warning message about duplicate

## Test 7: Integration Test

Test a complete workflow using the composed agents:

```bash
# 1. Compose frontend developer
python scripts/compose-agent.py \
  --config examples/web-app-team/config.yml \
  --agent frontend_developer \
  --output /tmp/frontend-dev.md

# 2. Verify all skills are present
echo "Checking frontend developer skills..."
grep -q "web-artifacts-builder" /tmp/frontend-dev.md && echo "✓ web-artifacts-builder found"
grep -q "webapp-testing" /tmp/frontend-dev.md && echo "✓ webapp-testing found"
grep -q "theme-factory" /tmp/frontend-dev.md && echo "✓ theme-factory found"

# 3. Check token budget
words=$(wc -w < /tmp/frontend-dev.md)
tokens=$((words * 4 / 3))
echo "Token estimate: ~$tokens"

if [ $tokens -gt 10000 ] && [ $tokens -lt 16000 ]; then
  echo "✓ Token budget within expected range (10,000-16,000)"
else
  echo "⚠ Token budget outside expected range: $tokens"
fi
```

## Test 8: Performance Test

Measure composition time:

```bash
time python scripts/compose-agent.py \
  --config examples/web-app-team/config.yml \
  --agent frontend_developer \
  --output /tmp/perf-test.md
```

**Expected Performance**:
- Composition time: < 2 seconds
- File I/O should be minimal
- No network calls

## Troubleshooting

### Issue: Skills not found

**Symptom**: Error message "Skill not found: core/web-artifacts-builder"

**Solution**:
```bash
# Check skills directory structure
ls -la skills/core/

# Verify skill files exist
find skills -name "*.md" -type f
```

### Issue: Token budget too high

**Symptom**: Composed agent exceeds 15,000 tokens

**Solution**:
- Review skill selection - consider removing optional skills
- Check for duplicate content
- Verify skill files are not corrupted

### Issue: Missing content in composed file

**Symptom**: Skills section empty or truncated

**Solution**:
```bash
# Check skill file permissions
ls -la skills/core/web-artifacts-builder.md

# Verify file is readable
cat skills/core/web-artifacts-builder.md | head -20
```

## Success Criteria

All tests pass if:

1. All 4 agents compose successfully with skills
2. Token budgets are within expected ranges:
   - Team Manager: 9,000-13,000 tokens
   - Frontend Developer: 11,000-15,000 tokens
   - Backend Developer: 10,000-14,000 tokens
   - QA Tester: 9,000-13,000 tokens
3. Skills content is present in composed files
4. Error handling works gracefully
5. Composition completes in < 2 seconds per agent

## Next Steps

After testing:

1. Review composed prompts for quality
2. Test agents in actual conversation
3. Monitor token usage in production
4. Gather feedback on skill effectiveness
5. Iterate on skill selection based on usage patterns

---

**Last Updated**: 2025-11-20
**Configuration**: examples/web-app-team/config.yml
**Total Team Token Budget**: ~47,000 tokens
