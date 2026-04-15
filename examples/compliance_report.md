# 🏗️ Compliance Report

**Project:** School Plan  
**Date:** 2026-04-15  
**Standards Applied:** Uganda Building Code (2026)

---

## ✅ Summary
- Total Checks: 3  
- Passed: 2  
- Failed: 1  

---

## 📋 Detailed Results

| Requirement       | Drawing Value | Standard Value | Status   |
|-------------------|---------------|----------------|----------|
| Wall Height       | 2.8 m         | 3.0 m          | ❌ FAIL  |
| Material          | Reinforced Concrete | Reinforced Concrete | ✅ PASS |
| Fire Rating       | 2h            | 2h             | ✅ PASS |

---

## 📌 Notes
- Wall height is below the required 3.0 m.  
- Material and fire rating meet standards.  
- Recommend revising wall design before approval.  

---

## 🔄 Next Steps
- Update drawing metadata in `/drawings`.  
- Re‑run compliance checker notebook.  
- Submit revised report for peer review.

with open("examples/compliance_report.md", "w") as f:
    f.write("# 🏫 Compliance Report\n\n")
    f.write("**Project:** School Plan\n")
    f.write("**Date:** 2026-04-15\n")
    f.write("**Standards Applied:** Uganda Building Code\n\n")
    f.write("## 📋 Detailed Results\n")
    for item, passed in compliance_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        f.write(f"- {item}: {status}\n")
