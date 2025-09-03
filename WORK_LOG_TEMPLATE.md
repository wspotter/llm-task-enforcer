# 📋 SuperManUS Mandatory Work Log Template
## Every Change Must Be Documented Using This Template

**Purpose:** Prevent LLM confusion and false completion claims through systematic validation

---

## 🚨 MANDATORY PRE-WORK CHECKLIST
Before starting ANY task, the LLM MUST:

- [ ] Read current SESSION_STATE.json
- [ ] Verify task is actually in active_tasks (not imaginary)  
- [ ] Check for dependencies/blockers
- [ ] Confirm required tools/environment available
- [ ] State expected deliverables clearly

---

## 📝 WORK LOG ENTRY TEMPLATE

### Task Information
- **Task ID:** [e.g., T3.2.1.1]  
- **Task Description:** [Exact wording from task list]
- **Start Time:** [ISO timestamp]
- **Estimated Duration:** [realistic estimate]
- **Dependencies:** [list any prerequisites]

### Pre-Work Validation
- **Environment Check:** [tools, connections, files available]
- **Dependency Status:** [all prerequisites met]
- **Clear Success Criteria:** [what constitutes "done"]

### Work Performed
#### Step 1: [Action Description]
- **Command/Action:** [exact command or operation]
- **Expected Result:** [what should happen]
- **Actual Result:** [what actually happened]
- **Validation:** [how was success confirmed]
- **Files Created/Modified:** [complete list with paths]

#### Step 2: [Action Description]  
- **Command/Action:** 
- **Expected Result:**
- **Actual Result:** 
- **Validation:**
- **Files Created/Modified:**

[Repeat for each step...]

### Final Validation
- [ ] **Syntax Check:** All files pass syntax validation
- [ ] **Functional Test:** Feature works as intended
- [ ] **Integration Test:** Works with existing system
- [ ] **Documentation:** All changes documented with context markers
- [ ] **Cleanup:** No temporary files or broken states left

### Completion Proof
- **Test Command:** [exact command that proves it works]
- **Test Output:** [paste actual output]  
- **Verification Screenshots/Logs:** [if applicable]
- **File Checksums:** [for critical files]

### Session State Updates
- **Tasks Completed:** [list with validation proof]
- **Tasks Still Active:** [remaining work]
- **Blockers Encountered:** [any issues found]
- **Next Session Notes:** [critical handoff information]

---

## ⚠️ COMPLETION CRITERIA
A task is NOT complete until:

1. ✅ All validation steps pass with proof
2. ✅ Documentation includes context markers per MASTER_PLAN
3. ✅ SESSION_STATE.json updated with proof
4. ✅ Future LLM can understand and continue work  
5. ✅ No false claims or assumptions made

---

## 🚫 FORBIDDEN ACTIONS

### NEVER claim completion without:
- Actual execution proof (not just "should work")
- File existence verification (not just Write tool success)
- Syntax/functional validation (not just import success)
- Real test results (not just theoretical correctness)

### NEVER say:
- "This should work" (test it)
- "Implementation is complete" (prove it)  
- "Production ready" (validate it)
- "Comprehensive" (count actual deliverables)

---

## 📊 VALIDATION COMMAND EXAMPLES

### File Existence
```bash
ls -la path/to/file && echo "✅ File exists" || echo "❌ File missing"
```

### Syntax Check
```bash
python -m py_compile file.py && echo "✅ Python syntax valid" || echo "❌ Syntax errors"
```

### Docker Compose
```bash
docker-compose config >/dev/null 2>&1 && echo "✅ Config valid" || echo "❌ Config errors"
```

### Kubernetes Manifests
```bash
kubectl apply --dry-run=client --validate=true -f manifest.yaml
```

### Service Response
```bash
curl -f http://service:8000/health && echo "✅ Service healthy" || echo "❌ Service down"
```

---

## 🦸 SuperManUS Anti-Confusion Pledge

*"I solemnly swear to validate before claiming, document before proceeding, and never leave future LLMs confused about the actual state of the system. With great code comes great responsibility for truth in reporting."*

---

**Template Version:** 1.0  
**Created:** 2025-09-03  
**Mandatory Use:** All SuperManUS development tasks