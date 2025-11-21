# Testing Skills Showcase Configurations

Comprehensive testing guide for all 10 skill configurations in the skills-showcase example.

## Quick Start

```bash
# Compose all configurations at once
cd /path/to/AI_agents

for agent in minimal_developer testing_specialist frontend_specialist \
             fullstack_developer qa_engineer engineering_manager \
             system_architect ui_ux_developer technical_writer \
             polyglot_developer; do
  python scripts/compose-agent.py \
    --config examples/skills-showcase/config.yml \
    --agent $agent \
    --output /tmp/showcase-$agent.md
done
```

## Test Suite 1: Individual Agent Composition

### Test 1.1: Minimal Developer (Baseline)

```bash
python scripts/compose-agent.py \
  --config examples/skills-showcase/config.yml \
  --agent minimal_developer \
  --output /tmp/minimal.md
```

**Expected Output**:
```
Loading configuration from examples/skills-showcase/config.yml
Composing agent: minimal_developer
  ✓ Loaded base: base/software-developer.md
  ✓ Wrote composed prompt to /tmp/minimal.md

Token estimate: ~3,000 tokens
```

**Verification**:
```bash
# Should have base content only
wc -w /tmp/minimal.md  # Expected: ~2,250 words (3,000 tokens)

# Should NOT have any skill markers
grep -c "## Skill:" /tmp/minimal.md  # Expected: 0

# Should have base software developer content
grep -c "software" /tmp/minimal.md  # Expected: > 0
```

**Success Criteria**:
- Token count: 2,500-3,500 tokens
- No skill sections
- Base developer knowledge present

---

### Test 1.2: Testing Specialist (Single Skill)

```bash
python scripts/compose-agent.py \
  --config examples/skills-showcase/config.yml \
  --agent testing_specialist \
  --output /tmp/testing-specialist.md
```

**Expected Output**:
```
Loading configuration from examples/skills-showcase/config.yml
Composing agent: testing_specialist
  ✓ Loaded base: base/qa-tester.md
  ✓ Loaded skill: core/webapp-testing
  ✓ Wrote composed prompt to /tmp/testing-specialist.md

Token estimate: ~7,000 tokens
```

**Verification**:
```bash
# Verify webapp-testing skill is included
grep -c "Playwright" /tmp/testing-specialist.md  # Expected: > 0
grep -c "webapp-testing" /tmp/testing-specialist.md  # Expected: > 0

# Verify token budget (roughly)
words=$(wc -w < /tmp/testing-specialist.md)
tokens=$((words * 4 / 3))
echo "Token estimate: ~$tokens"  # Expected: 6,000-8,000
```

**Success Criteria**:
- Token count: 6,000-8,000 tokens
- Playwright content present
- QA tester base + testing skill

---

### Test 1.3: Frontend Specialist (Standard Configuration)

```bash
python scripts/compose-agent.py \
  --config examples/skills-showcase/config.yml \
  --agent frontend_specialist \
  --output /tmp/frontend-specialist.md
```

**Expected Output**:
```
Loading configuration from examples/skills-showcase/config.yml
Composing agent: frontend_specialist
  ✓ Loaded base: base/software-developer.md
  ✓ Loaded platform: platforms/web/frontend-developer.md
  ✓ Loaded skill: core/web-artifacts-builder
  ✓ Loaded skill: design/theme-factory
  ✓ Loaded skill: core/webapp-testing
  ✓ Wrote composed prompt to /tmp/frontend-specialist.md

Token estimate: ~13,000 tokens
```

**Verification**:
```bash
# Check all components are present
grep -c "React" /tmp/frontend-specialist.md  # Platform content
grep -c "web-artifacts-builder" /tmp/frontend-specialist.md  # Skill 1
grep -c "theme-factory" /tmp/frontend-specialist.md  # Skill 2
grep -c "Playwright" /tmp/frontend-specialist.md  # Skill 3

# Verify token budget
words=$(wc -w < /tmp/frontend-specialist.md)
tokens=$((words * 4 / 3))
echo "Token estimate: ~$tokens"  # Expected: 11,000-15,000
```

**Success Criteria**:
- Token count: 11,000-15,000 tokens
- Base + platform + 3 skills present
- All frontend capabilities available

---

### Test 1.4: Full-Stack Developer (Advanced)

```bash
python scripts/compose-agent.py \
  --config examples/skills-showcase/config.yml \
  --agent fullstack_developer \
  --output /tmp/fullstack.md
```

**Expected Output**:
```
Composing agent: fullstack_developer
  ✓ Loaded base: base/software-developer.md
  ✓ Loaded platform: platforms/web/frontend-developer.md
  ✓ Loaded platform: platforms/web/backend-developer.md
  ✓ Loaded skill: core/web-artifacts-builder
  ✓ Loaded skill: core/mcp-builder
  ✓ Loaded skill: core/webapp-testing

Token estimate: ~16,000 tokens
```

**Verification**:
```bash
# Verify both platforms loaded
grep -c "frontend-developer" /tmp/fullstack.md  # Expected: > 0
grep -c "backend-developer" /tmp/fullstack.md  # Expected: > 0

# Verify cross-domain skills
grep -c "web-artifacts-builder" /tmp/fullstack.md  # Frontend
grep -c "mcp-builder" /tmp/fullstack.md  # Backend
grep -c "Playwright" /tmp/fullstack.md  # Testing

# Token check
words=$(wc -w < /tmp/fullstack.md)
tokens=$((words * 4 / 3))
echo "Token estimate: ~$tokens"  # Expected: 14,000-18,000
```

**Success Criteria**:
- Token count: 14,000-18,000 tokens
- Both platforms loaded
- Frontend and backend skills present

---

### Test 1.5: All Other Configurations

```bash
# QA Engineer
python scripts/compose-agent.py \
  --config examples/skills-showcase/config.yml \
  --agent qa_engineer \
  --output /tmp/qa-engineer.md

# Engineering Manager
python scripts/compose-agent.py \
  --config examples/skills-showcase/config.yml \
  --agent engineering_manager \
  --output /tmp/manager.md

# System Architect
python scripts/compose-agent.py \
  --config examples/skills-showcase/config.yml \
  --agent system_architect \
  --output /tmp/architect.md

# UI/UX Developer
python scripts/compose-agent.py \
  --config examples/skills-showcase/config.yml \
  --agent ui_ux_developer \
  --output /tmp/ui-ux.md

# Technical Writer
python scripts/compose-agent.py \
  --config examples/skills-showcase/config.yml \
  --agent technical_writer \
  --output /tmp/tech-writer.md

# Polyglot Developer (max skills)
python scripts/compose-agent.py \
  --config examples/skills-showcase/config.yml \
  --agent polyglot_developer \
  --output /tmp/polyglot.md
```

**Quick Verification**:
```bash
# Check all files were created
ls -lh /tmp/showcase-*.md /tmp/minimal.md /tmp/testing-specialist.md \
       /tmp/frontend-specialist.md /tmp/fullstack.md /tmp/qa-engineer.md \
       /tmp/manager.md /tmp/architect.md /tmp/ui-ux.md \
       /tmp/tech-writer.md /tmp/polyglot.md
```

---

## Test Suite 2: Token Budget Analysis

### Test 2.1: Comprehensive Token Budget Report

```bash
#!/bin/bash
echo "Skills Showcase Token Budget Report"
echo "===================================="
echo ""
printf "%-25s %10s %10s %8s\n" "Configuration" "Words" "Tokens" "Skills"
echo "----------------------------------------------------------------"

configs=(
  "minimal_developer:0"
  "testing_specialist:1"
  "frontend_specialist:3"
  "fullstack_developer:3"
  "qa_engineer:4"
  "engineering_manager:4"
  "system_architect:4"
  "ui_ux_developer:4"
  "technical_writer:4"
  "polyglot_developer:6"
)

total_tokens=0

for config in "${configs[@]}"; do
  agent="${config%:*}"
  skills="${config#*:}"

  if [ "$agent" = "minimal_developer" ]; then
    file="/tmp/minimal.md"
  elif [ "$agent" = "testing_specialist" ]; then
    file="/tmp/testing-specialist.md"
  elif [ "$agent" = "frontend_specialist" ]; then
    file="/tmp/frontend-specialist.md"
  elif [ "$agent" = "fullstack_developer" ]; then
    file="/tmp/fullstack.md"
  elif [ "$agent" = "qa_engineer" ]; then
    file="/tmp/qa-engineer.md"
  elif [ "$agent" = "engineering_manager" ]; then
    file="/tmp/manager.md"
  elif [ "$agent" = "system_architect" ]; then
    file="/tmp/architect.md"
  elif [ "$agent" = "ui_ux_developer" ]; then
    file="/tmp/ui-ux.md"
  elif [ "$agent" = "technical_writer" ]; then
    file="/tmp/tech-writer.md"
  else
    file="/tmp/polyglot.md"
  fi

  if [ -f "$file" ]; then
    words=$(wc -w < "$file")
    tokens=$((words * 4 / 3))
    total_tokens=$((total_tokens + tokens))
    printf "%-25s %10d %10d %8s\n" "$agent" "$words" "$tokens" "$skills"
  fi
done

echo "----------------------------------------------------------------"
echo "Total if all agents used: ~$total_tokens tokens"
echo ""
```

**Expected Output**:
```
Skills Showcase Token Budget Report
====================================

Configuration                  Words     Tokens   Skills
----------------------------------------------------------------
minimal_developer               2250       3000        0
testing_specialist              5250       7000        1
frontend_specialist             9750      13000        3
fullstack_developer            12000      16000        3
qa_engineer                    10500      14000        4
engineering_manager            10500      14000        4
system_architect               12750      17000        4
ui_ux_developer                10500      14000        4
technical_writer                9750      13000        4
polyglot_developer             15000      20000        6
----------------------------------------------------------------
Total if all agents used: ~131,000 tokens
```

---

## Test Suite 3: Skill Content Verification

### Test 3.1: Verify Skill Uniqueness

Ensure skills are included in the right agents and not duplicated:

```bash
# web-artifacts-builder should be in:
# - frontend_specialist, fullstack_developer, ui_ux_developer, polyglot_developer
echo "web-artifacts-builder occurrences:"
grep -c "web-artifacts-builder" /tmp/frontend-specialist.md  # Should be > 0
grep -c "web-artifacts-builder" /tmp/fullstack.md  # Should be > 0
grep -c "web-artifacts-builder" /tmp/manager.md  # Should be 0

# mcp-builder should be in:
# - fullstack_developer, system_architect, polyglot_developer
echo "mcp-builder occurrences:"
grep -c "mcp-builder" /tmp/fullstack.md  # Should be > 0
grep -c "mcp-builder" /tmp/architect.md  # Should be > 0
grep -c "mcp-builder" /tmp/frontend-specialist.md  # Should be 0

# internal-comms should be in:
# - engineering_manager, system_architect, technical_writer, polyglot_developer
echo "internal-comms occurrences:"
grep -c "internal-comms" /tmp/manager.md  # Should be > 0
grep -c "internal-comms" /tmp/architect.md  # Should be > 0
grep -c "internal-comms" /tmp/frontend-specialist.md  # Should be 0
```

---

### Test 3.2: Verify Skill Content Quality

Check that skills include their key content:

```bash
# web-artifacts-builder should mention React and Tailwind
grep -q "React" /tmp/frontend-specialist.md && echo "✓ React found"
grep -q "Tailwind" /tmp/frontend-specialist.md && echo "✓ Tailwind found"

# mcp-builder should mention FastMCP or TypeScript
grep -q "FastMCP\|TypeScript" /tmp/fullstack.md && echo "✓ MCP SDK references found"

# webapp-testing should mention Playwright
grep -q "Playwright" /tmp/testing-specialist.md && echo "✓ Playwright found"

# theme-factory should mention themes
grep -q "theme" /tmp/frontend-specialist.md && echo "✓ Theme content found"

# skill-creator should mention skill design
grep -q "skill.*design\|SKILL.md" /tmp/architect.md && echo "✓ Skill creator content found"
```

---

## Test Suite 4: Comparative Analysis

### Test 4.1: Minimal vs Skilled Comparison

```bash
# Compare minimal developer to frontend specialist
echo "Minimal Developer:"
wc -w /tmp/minimal.md

echo "Frontend Specialist:"
wc -w /tmp/frontend-specialist.md

minimal_words=$(wc -w < /tmp/minimal.md)
frontend_words=$(wc -w < /tmp/frontend-specialist.md)
diff_words=$((frontend_words - minimal_words))
diff_tokens=$((diff_words * 4 / 3))

echo "Skills add: $diff_words words (~$diff_tokens tokens)"
percentage=$(((frontend_words - minimal_words) * 100 / minimal_words))
echo "Percentage increase: $percentage%"
```

**Expected**: ~333% increase (7,500 words / 10,000 tokens added)

---

### Test 4.2: Single Skill vs Multiple Skills

```bash
# Testing Specialist (1 skill) vs QA Engineer (4 skills)
testing_words=$(wc -w < /tmp/testing-specialist.md)
qa_words=$(wc -w < /tmp/qa-engineer.md)

echo "Testing Specialist (1 skill): $testing_words words"
echo "QA Engineer (4 skills): $qa_words words"
echo "Adding 3 more skills adds: $((qa_words - testing_words)) words"
```

**Expected**: ~5,250 words difference (~7,000 tokens for 3 additional skills)

---

### Test 4.3: Frontend vs Full-Stack

```bash
# Compare frontend specialist to full-stack developer
frontend_words=$(wc -w < /tmp/frontend-specialist.md)
fullstack_words=$(wc -w < /tmp/fullstack.md)

echo "Frontend Specialist: $frontend_words words"
echo "Full-Stack Developer: $fullstack_words words"
echo "Adding backend adds: $((fullstack_words - frontend_words)) words"
```

**Expected**: ~2,250 words difference (~3,000 tokens for backend platform + skill swap)

---

## Test Suite 5: Performance Testing

### Test 5.1: Composition Speed

```bash
# Time each agent composition
echo "Composition Speed Test"
echo "======================"

for agent in minimal_developer testing_specialist frontend_specialist \
             fullstack_developer qa_engineer; do
  echo -n "$agent: "
  time python scripts/compose-agent.py \
    --config examples/skills-showcase/config.yml \
    --agent $agent \
    --output /tmp/perf-$agent.md 2>&1 > /dev/null
done
```

**Expected Performance**:
- Minimal: < 0.5 seconds
- Testing Specialist: < 1 second
- Frontend Specialist: < 1.5 seconds
- Full-Stack: < 2 seconds
- Complex (4+ skills): < 2.5 seconds

---

### Test 5.2: Memory Usage

```bash
# Monitor memory during composition of largest configuration
/usr/bin/time -l python scripts/compose-agent.py \
  --config examples/skills-showcase/config.yml \
  --agent polyglot_developer \
  --output /tmp/polyglot-mem-test.md
```

**Expected**: < 50MB memory usage for composition

---

## Test Suite 6: Validation Tests

### Test 6.1: YAML Syntax Validation

```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('examples/skills-showcase/config.yml'))" \
  && echo "✓ YAML syntax valid" \
  || echo "✗ YAML syntax error"
```

---

### Test 6.2: All Skills Exist

```bash
# Check that all referenced skills exist
echo "Verifying all skills exist..."

skills=(
  "core/web-artifacts-builder"
  "core/webapp-testing"
  "core/mcp-builder"
  "core/skill-creator"
  "design/theme-factory"
  "design/algorithmic-art"
  "design/canvas-design"
  "documents/docx"
  "documents/pdf"
  "documents/xlsx"
  "documents/pptx"
  "communication/internal-comms"
)

for skill in "${skills[@]}"; do
  if [ -f "skills/$skill.md" ]; then
    echo "  ✓ $skill"
  else
    echo "  ✗ $skill MISSING"
  fi
done
```

---

### Test 6.3: No Duplicate Skills

```bash
# Verify no agent has duplicate skills
python << 'EOF'
import yaml

with open('examples/skills-showcase/config.yml') as f:
    config = yaml.safe_load(f)

for agent_name, agent_config in config['agents'].items():
    if 'skills' in agent_config:
        skills = agent_config['skills']
        if len(skills) != len(set(skills)):
            print(f"✗ {agent_name} has duplicate skills")
        else:
            print(f"✓ {agent_name} has no duplicates")
    else:
        print(f"  {agent_name} has no skills")
EOF
```

---

## Test Suite 7: Integration Tests

### Test 7.1: Complete Showcase Test

```bash
#!/bin/bash
echo "Running Complete Skills Showcase Test"
echo "======================================"
echo ""

# Step 1: Compose all agents
echo "Step 1: Composing all 10 agent configurations..."
success=0
fail=0

agents=(
  "minimal_developer"
  "testing_specialist"
  "frontend_specialist"
  "fullstack_developer"
  "qa_engineer"
  "engineering_manager"
  "system_architect"
  "ui_ux_developer"
  "technical_writer"
  "polyglot_developer"
)

for agent in "${agents[@]}"; do
  python scripts/compose-agent.py \
    --config examples/skills-showcase/config.yml \
    --agent $agent \
    --output /tmp/showcase-$agent.md 2>&1 > /dev/null

  if [ $? -eq 0 ]; then
    echo "  ✓ $agent"
    ((success++))
  else
    echo "  ✗ $agent FAILED"
    ((fail++))
  fi
done

echo ""
echo "Results: $success/10 agents composed successfully"

# Step 2: Verify token budgets
echo ""
echo "Step 2: Verifying token budgets..."

expected_budgets=(
  "minimal_developer:2500-3500"
  "testing_specialist:6000-8000"
  "frontend_specialist:11000-15000"
  "fullstack_developer:14000-18000"
  "qa_engineer:12000-16000"
  "engineering_manager:12000-16000"
  "system_architect:15000-19000"
  "ui_ux_developer:12000-16000"
  "technical_writer:11000-15000"
  "polyglot_developer:18000-22000"
)

for budget in "${expected_budgets[@]}"; do
  agent="${budget%:*}"
  range="${budget#*:}"
  min="${range%-*}"
  max="${range#*-}"

  words=$(wc -w < /tmp/showcase-$agent.md)
  tokens=$((words * 4 / 3))

  if [ $tokens -ge $min ] && [ $tokens -le $max ]; then
    echo "  ✓ $agent: $tokens tokens (within $min-$max)"
  else
    echo "  ⚠ $agent: $tokens tokens (expected $min-$max)"
  fi
done

# Step 3: Verify skills present
echo ""
echo "Step 3: Spot-checking skill presence..."
grep -q "web-artifacts-builder" /tmp/showcase-frontend_specialist.md && \
  echo "  ✓ Frontend has web-artifacts-builder"
grep -q "mcp-builder" /tmp/showcase-fullstack_developer.md && \
  echo "  ✓ Full-stack has mcp-builder"
grep -q "internal-comms" /tmp/showcase-engineering_manager.md && \
  echo "  ✓ Manager has internal-comms"

echo ""
echo "Integration test complete!"
```

---

## Success Criteria

All tests pass if:

### Composition Tests
- ✓ All 10 agents compose without errors
- ✓ All agents produce output files
- ✓ No Python/YAML syntax errors

### Token Budget Tests
- ✓ Minimal developer: 2,500-3,500 tokens
- ✓ Single skill: 6,000-8,000 tokens
- ✓ Standard (2-3 skills): 11,000-15,000 tokens
- ✓ Advanced (4 skills): 12,000-17,000 tokens
- ✓ Maximum (6 skills): 18,000-22,000 tokens

### Content Tests
- ✓ All referenced skills are included
- ✓ No duplicate skills in any agent
- ✓ Skills contain expected keywords (React, Playwright, etc.)

### Performance Tests
- ✓ Composition time < 2 seconds per agent
- ✓ Memory usage < 50MB
- ✓ No file I/O errors

---

## Troubleshooting

### Issue: Agent fails to compose

**Check**:
```bash
# Verify config syntax
python -c "import yaml; print(yaml.safe_load(open('examples/skills-showcase/config.yml')))"

# Check referenced files exist
ls -la base/
ls -la platforms/
ls -la skills/
```

### Issue: Token budget out of range

**Cause**: Skill files may be missing or corrupted

**Solution**:
```bash
# Verify all skill files
find skills -name "*.md" -type f -exec wc -l {} \;

# Re-compose with verbose output
python scripts/compose-agent.py \
  --config examples/skills-showcase/config.yml \
  --agent frontend_specialist \
  --output /tmp/test.md \
  --verbose
```

### Issue: Skills not appearing in output

**Check**:
```bash
# Verify skill path in config
grep -A5 "frontend_specialist:" examples/skills-showcase/config.yml

# Check if skill file exists
ls -la skills/core/web-artifacts-builder.md
```

---

**Last Updated**: 2025-11-20
**Total Configurations**: 10
**Total Test Cases**: 30+
