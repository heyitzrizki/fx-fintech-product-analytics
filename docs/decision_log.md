# Decision Log

These are deliberate scope choices, not claims that each method is universally best. The goal is to keep the analysis explainable, reproducible, and tied to a product decision.

| Decision | Reason |
|---|---|
| One main workbook | Gives reviewers one clear analytical path; earlier exploration is kept only in the archive |
| Yahoo Finance FX snapshot with local cache | Uses real historical market observations while keeping repeated runs reproducible |
| Chronological model splits | Prevents future periods from informing earlier validation |
| Four repeat-model features | Uses fields available at the observation date and avoids ambiguous lifetime leakage |
| Interpretation-aware model selection | A small metric gain does not automatically justify a harder-to-explain model |
| Simulated experiment labeled explicitly | Demonstrates statistical evaluation without claiming production causal evidence |
| Scenario campaign value | Low/base/high assumptions expose sensitivity and avoid revenue claims |
| Six dashboard pages | Each page maps to a distinct product or operating decision |
| Earlier notebooks moved to `notebooks/archive/` | Preserves prior exploration while keeping one clear notebook entry point |
