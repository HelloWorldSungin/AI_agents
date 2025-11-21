# Testing Mobile App Team Configuration

This guide shows how to test the mobile-app-team configuration with skills integration.

## Prerequisites

```bash
# Ensure AI Agents library is installed
cd /path/to/AI_agents

# Verify skills directory exists
ls -la skills/core/ skills/design/ skills/documents/ skills/communication/
```

## Test 1: Compose Mobile Team Agents

### Mobile Developer with Skills

```bash
python scripts/compose-agent.py \
  --config examples/mobile-app-team/config.yml \
  --agent mobile_developer \
  --output /tmp/mobile-dev-composed.md
```

**Expected Output**:
```
Loading configuration from examples/mobile-app-team/config.yml
Composing agent: mobile_developer
  ✓ Loaded base: base/software-developer.md
  ✓ Loaded platform: platforms/mobile/mobile-developer.md
  ✓ Loaded platform: platforms/web/frontend-developer.md
  ✓ Loaded skill: design/theme-factory
  ✓ Loaded skill: core/web-artifacts-builder
  ✓ Loaded skill: core/skill-creator
  ✓ Wrote composed prompt to /tmp/mobile-dev-composed.md

Token estimate: ~16,000 tokens
```

**Verification**:
```bash
# Verify mobile-specific content
grep -c "React Native" /tmp/mobile-dev-composed.md  # Should be > 0
grep -c "theme-factory" /tmp/mobile-dev-composed.md  # Should be > 0
grep -c "web-artifacts-builder" /tmp/mobile-dev-composed.md  # Should be > 0

# Check token budget
words=$(wc -w < /tmp/mobile-dev-composed.md)
tokens=$((words * 4 / 3))
echo "Token estimate: ~$tokens"
# Should be 14,000-18,000 tokens
```

### Architect with Skills

```bash
python scripts/compose-agent.py \
  --config examples/mobile-app-team/config.yml \
  --agent architect \
  --output /tmp/architect-composed.md
```

**Expected Output**:
```
Loading configuration from examples/mobile-app-team/config.yml
Composing agent: architect
  ✓ Loaded base: base/architect.md
  ✓ Loaded platform: platforms/mobile/mobile-developer.md
  ✓ Loaded skill: core/skill-creator
  ✓ Loaded skill: documents/pptx
  ✓ Loaded skill: communication/internal-comms
  ✓ Wrote composed prompt to /tmp/architect-composed.md

Token estimate: ~14,000 tokens
```

**Verification**:
```bash
grep -c "skill-creator" /tmp/architect-composed.md  # Should be > 0
grep -c "pptx" /tmp/architect-composed.md           # Should be > 0
grep -c "architecture" /tmp/architect-composed.md   # Should be > 0
```

### Team Manager with Skills

```bash
python scripts/compose-agent.py \
  --config examples/mobile-app-team/config.yml \
  --agent team_manager \
  --output /tmp/mobile-manager-composed.md
```

**Expected Output**:
```
Loading configuration from examples/mobile-app-team/config.yml
Composing agent: team_manager
  ✓ Loaded base: base/manager.md
  ✓ Loaded skill: communication/internal-comms
  ✓ Loaded skill: documents/pptx
  ✓ Loaded skill: documents/xlsx
  ✓ Wrote composed prompt to /tmp/mobile-manager-composed.md

Token estimate: ~12,000 tokens
```

**Verification**:
```bash
grep -c "release" /tmp/mobile-manager-composed.md  # Should be > 0
grep -c "3P update" /tmp/mobile-manager-composed.md  # Should be > 0
grep -c "xlsx" /tmp/mobile-manager-composed.md  # Should be > 0
```

## Test 2: Compose All Agents

```bash
# Compose all 5 agents
for agent in team_manager mobile_developer backend_developer architect qa_tester; do
  echo "Composing $agent..."
  python scripts/compose-agent.py \
    --config examples/mobile-app-team/config.yml \
    --agent $agent \
    --output /tmp/mobile-$agent-composed.md
done
```

**Expected Outcome**: All 5 agents successfully composed

## Test 3: Token Budget Analysis

```bash
# Analyze token budget for entire team
echo "Mobile App Team Token Budget Analysis"
echo "======================================"
total_tokens=0

for agent in team_manager mobile_developer backend_developer architect qa_tester; do
  file="/tmp/mobile-$agent-composed.md"
  if [ -f "$file" ]; then
    words=$(wc -w < "$file")
    tokens=$((words * 4 / 3))
    total_tokens=$((total_tokens + tokens))
    printf "%-20s: ~%6d tokens (%6d words)\n" "$agent" "$tokens" "$words"
  fi
done

echo "======================================"
echo "Total Team Budget   : ~$total_tokens tokens"
```

**Expected Output**:
```
Mobile App Team Token Budget Analysis
======================================
team_manager        : ~12,000 tokens (9,000 words)
mobile_developer    : ~16,000 tokens (12,000 words)
backend_developer   : ~12,000 tokens (9,000 words)
architect           : ~14,000 tokens (10,500 words)
qa_tester           : ~11,000 tokens (8,250 words)
======================================
Total Team Budget   : ~65,000 tokens
```

## Test 4: Mobile-Specific Skill Verification

### Test theme-factory in Mobile Developer

```bash
# Extract theme-factory skill section
sed -n '/theme-factory/,/## End Skill/p' \
  /tmp/mobile-dev-composed.md | head -30
```

**Expected Content**:
- 10 pre-set professional themes
- Custom theme generation
- Color palette and typography guidelines
- Mobile-appropriate design patterns

### Test skill-creator in Architect

```bash
# Extract skill-creator skill section
sed -n '/skill-creator/,/## End Skill/p' \
  /tmp/architect-composed.md | head -40
```

**Expected Content**:
- Skill design principles
- Progressive disclosure patterns
- SKILL.md formatting
- Mobile pattern documentation guidance

## Test 5: Platform Composition Verification

### Verify Mobile + Web Platform Loading

```bash
# Mobile developer should have both mobile and web platforms
grep -c "platforms/mobile/mobile-developer.md" /tmp/mobile-dev-composed.md  # Should be > 0
grep -c "platforms/web/frontend-developer.md" /tmp/mobile-dev-composed.md   # Should be > 0

# Check for React Native content
grep -c "React Native" /tmp/mobile-dev-composed.md  # Should be > 0
grep -c "iOS\|Android" /tmp/mobile-dev-composed.md  # Should be > 0
```

## Test 6: Skills Comparison

Compare agents with and without skills:

```bash
# Create minimal mobile developer (no skills)
cat > /tmp/minimal-mobile-config.yml << 'EOF'
agents:
  mobile_developer_minimal:
    base: "base/software-developer.md"
    platforms:
      - "platforms/mobile/mobile-developer.md"
      - "platforms/web/frontend-developer.md"
EOF

python scripts/compose-agent.py \
  --config /tmp/minimal-mobile-config.yml \
  --agent mobile_developer_minimal \
  --output /tmp/mobile-dev-minimal.md

# Compare sizes
echo "Without Skills:"
wc -w /tmp/mobile-dev-minimal.md

echo "With Skills:"
wc -w /tmp/mobile-dev-composed.md

# Calculate difference
minimal_words=$(wc -w < /tmp/mobile-dev-minimal.md)
full_words=$(wc -w < /tmp/mobile-dev-composed.md)
diff_words=$((full_words - minimal_words))
echo "Skills add approximately $diff_words words (~$((diff_words * 4 / 3)) tokens)"
```

**Expected Difference**: ~5,000-7,000 words (~7,000-9,000 tokens) added by skills

## Test 7: Mobile Release Workflow Test

Test manager's release workflow capabilities:

```bash
# Verify manager has release-related skills
grep -c "internal-comms" /tmp/mobile-manager-composed.md  # Release notes
grep -c "pptx" /tmp/mobile-manager-composed.md            # Stakeholder presentations
grep -c "xlsx" /tmp/mobile-manager-composed.md            # Metrics tracking

# All should be > 0 for effective release management
```

## Test 8: Integration Test

Complete workflow test:

```bash
#!/bin/bash
echo "Mobile Team Integration Test"
echo "============================"

# Test 1: Compose all agents
echo "Step 1: Composing all agents..."
success=0
for agent in team_manager mobile_developer backend_developer architect qa_tester; do
  python scripts/compose-agent.py \
    --config examples/mobile-app-team/config.yml \
    --agent $agent \
    --output /tmp/mobile-$agent.md 2>&1 > /dev/null

  if [ $? -eq 0 ]; then
    echo "  ✓ $agent composed successfully"
    ((success++))
  else
    echo "  ✗ $agent failed to compose"
  fi
done

echo ""
echo "Results: $success/5 agents composed successfully"

# Test 2: Verify skills presence
echo ""
echo "Step 2: Verifying skills..."
grep -q "theme-factory" /tmp/mobile-mobile_developer.md && echo "  ✓ Mobile dev has theme-factory"
grep -q "skill-creator" /tmp/mobile-architect.md && echo "  ✓ Architect has skill-creator"
grep -q "internal-comms" /tmp/mobile-team_manager.md && echo "  ✓ Manager has internal-comms"

# Test 3: Token budget check
echo ""
echo "Step 3: Token budget verification..."
total=0
for agent in team_manager mobile_developer backend_developer architect qa_tester; do
  words=$(wc -w < /tmp/mobile-$agent.md)
  tokens=$((words * 4 / 3))
  total=$((total + tokens))
done

if [ $total -gt 60000 ] && [ $total -lt 70000 ]; then
  echo "  ✓ Total budget within expected range: ~$total tokens"
else
  echo "  ⚠ Total budget outside expected range: ~$total tokens (expected 60,000-70,000)"
fi

echo ""
echo "Integration test complete!"
```

## Test 9: Mobile-Specific Features

### Test Device Matrix Awareness

```bash
# QA tester should be aware of device testing requirements
python scripts/compose-agent.py \
  --config examples/mobile-app-team/config.yml \
  --agent qa_tester \
  --output /tmp/mobile-qa.md

# Check for mobile testing capabilities
grep -c "device" /tmp/mobile-qa.md  # Should be > 0
grep -c "iOS\|Android" /tmp/mobile-qa.md  # Should be > 0
```

## Troubleshooting

### Issue: Theme-factory not loading for mobile developer

**Symptom**: Mobile developer missing theme-factory skill

**Solution**:
```bash
# Verify skill file exists
ls -la skills/design/theme-factory.md

# Check config syntax
grep -A5 "mobile_developer:" examples/mobile-app-team/config.yml
```

### Issue: High token budget

**Symptom**: Team exceeds 70,000 tokens

**Solution**:
- Review if all skills are necessary
- Consider removing tertiary skills
- Mobile developer could drop skill-creator if not creating custom patterns

### Issue: Platform conflicts

**Symptom**: Conflicting guidance from mobile and web platforms

**Solution**:
- This is expected for React Native (uses both)
- Mobile developer should prioritize mobile-specific patterns
- Web platform provides React knowledge applicable to React Native

## Performance Benchmarks

Expected composition times:

| Agent              | Composition Time | Token Count |
|--------------------|------------------|-------------|
| Team Manager       | < 1.5 sec        | ~12,000     |
| Mobile Developer   | < 2.0 sec        | ~16,000     |
| Backend Developer  | < 1.5 sec        | ~12,000     |
| Architect          | < 1.5 sec        | ~14,000     |
| QA Tester          | < 1.5 sec        | ~11,000     |
| **Total Team**     | **< 8 sec**      | **~65,000** |

## Success Criteria

All tests pass if:

1. All 5 agents compose successfully
2. Mobile developer has 16,000 ± 2,000 tokens
3. Total team budget is 65,000 ± 5,000 tokens
4. theme-factory present in mobile developer
5. skill-creator present in architect
6. internal-comms present in manager
7. Platform composition works correctly (mobile + web for mobile dev)
8. Composition completes in < 2 sec per agent

## Next Steps

After testing:

1. Test agents in actual mobile development scenarios
2. Verify React Native component generation works
3. Test theme application across iOS and Android
4. Validate release workflow with manager
5. Gather metrics on skill usage patterns

---

**Last Updated**: 2025-11-20
**Configuration**: examples/mobile-app-team/config.yml
**Total Team Token Budget**: ~65,000 tokens
