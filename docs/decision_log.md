# Decision Log

| Decision | Reason |
|---|---|
| One main workbook | Keeps the analytical narrative recruiter-readable while retaining prior notebooks as supporting work |
| Yahoo Finance FX snapshot with local cache | Uses real historical market observations while keeping repeated runs reproducible |
| Chronological model splits | Prevents future periods from informing earlier validation |
| Four repeat-model features | Uses fields available at the observation date and avoids ambiguous lifetime leakage |
| Interpretation-aware model selection | A small metric gain does not automatically justify a harder-to-explain model |
| Simulated experiment labeled explicitly | Demonstrates statistical evaluation without claiming production causal evidence |
| Scenario campaign value | Low/base/high assumptions expose sensitivity and avoid revenue claims |
| Six dashboard pages | Each page maps to a distinct product or operating decision |
| Existing notebooks retained | They preserve earlier exploratory work and are not required for the main workflow |
