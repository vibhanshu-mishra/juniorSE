# Example Use

Prompt to an AI agent:

> Use the juniorSE Skills library. Check whether W12x26 works as a simply supported non-composite steel beam spanning 20 ft with 1.0 kip/ft dead load and 2.0 kip/ft live load. Use LRFD, AISC 360-22, A992 steel, and assume continuous lateral bracing. Use L/360 live-load deflection limit.

Expected behavior:

1. Load `structural-response-protocol`.
2. Load `assumption-guardrails` and confirm whether any critical inputs are missing.
3. Load `select-load-combinations` to determine design demand.
4. Load `steel-beam-gravity-check` to perform the bounded member check.
5. Load `calculation-qaqc-review` before final response.

The agent should not skip directly to a final pass/fail.
