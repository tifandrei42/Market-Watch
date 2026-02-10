---
trigger: always_on
---

# Market Watch Dev Rules
- When I ask to "add a new agent," create its definition in `config/agents.yaml` first.
- Always ensure the `researcher` prioritizes my core stock list (NVIDIA, AMD, Palantir, etc.).
- When debugging, look at the `output/` folder for the latest generated report.
- Keep the Python code in `crew.py` modular using the @CrewBase decorators.