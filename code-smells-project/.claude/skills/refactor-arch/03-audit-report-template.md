# Audit Report Template

Use this exact format when generating the Phase 2 audit report. Do not skip sections.

---

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <project directory name>
Stack:   <Language> + <Framework version>
Files:   <N> analyzed | ~<total LOC> lines of code

Summary
CRITICAL: <N> | HIGH: <N> | MEDIUM: <N> | LOW: <N>

Findings
(ordered CRITICAL → HIGH → MEDIUM → LOW; within same severity, order by file/line)

---

[CRITICAL] <Anti-pattern Name from catalog>
File: <relative/path/to/file.py>:<start_line>-<end_line>
Description: <What exactly was found. Quote the offending code snippet (1–3 lines).>
Impact: <Concrete consequence if left unfixed.>
Recommendation: <Specific action to take — reference the playbook transformation if applicable.>

[CRITICAL] <Anti-pattern Name>
File: <path>:<lines>
Description: ...
Impact: ...
Recommendation: ...

[HIGH] <Anti-pattern Name>
File: <path>:<lines>
Description: ...
Impact: ...
Recommendation: ...

[MEDIUM] <Anti-pattern Name>
File: <path>:<lines>
Description: ...
Impact: ...
Recommendation: ...

[LOW] <Anti-pattern Name>
File: <path>:<lines>
Description: ...
Impact: ...
Recommendation: ...

---

================================
Total: <N> findings
CRITICAL: <N> | HIGH: <N> | MEDIUM: <N> | LOW: <N>
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## Filling-in Guidelines

- **File paths** must be relative to the project root (e.g., `src/app.js`, `models.py`).
- **Line numbers** must be exact — read the file and count.
- **Description** must quote the specific offending code (not paraphrase). Example:
  ```
  Description: Line 28 executes a query via string concatenation:
               cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
  ```
- **Never aggregate** two different anti-patterns into a single finding. One finding = one anti-pattern instance.
- **Order within same severity** by file name, then by line number (ascending).
- **Deprecated API** must always be reported when found, even if the code still works.
- **Minimum**: 5 findings per project; at least 1 must be CRITICAL or HIGH.
