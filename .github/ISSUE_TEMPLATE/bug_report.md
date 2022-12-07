---
name: Bug report
about: Create a report to help us improve
title: ''
labels: ''
assignees: ralequi

---

**Describe the bug**
A clear and concise description of what the bug is.

**Raw outputs**
Please, provide the following raw command outputs to be added to our test-base. Notify explicitly if you don't want them to be incorporated. In any case, they are "mostly required" to check and verify your issue/bug.

- `smartctl --scan-open`
- `smartctl --all <problematic device> # Example: smartctl --all /dev/nvme0`

**Environmental setup:**
 - Complete smartctl version [e.g. `smartctl 7.3 2022-02-28 r5338 [x86_64-linux-6.0.10-300.fc37.x86_64]`]
 - Py-SMART version [e.g. `v1.2.0`]

**Additional context**
Add any other context about the problem here.
