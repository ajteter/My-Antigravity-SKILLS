# Steam FX Card Optimization Notes

## Scope

This document records the main improvements made to the `steam-fx-card` skill across trigger design, script robustness, and maintainability.

## What Was Improved

### 1. Skill triggering became broader and more realistic

The original trigger description focused mainly on direct amount inputs such as `US$5.00`. That was too narrow for real-world usage because users often ask in less structured ways, for example:

- "Steam 美区和日区哪个更便宜"
- "阿区这个价格折合人民币多少"
- "帮我看跨区哪个区最省"

The skill description now explicitly covers:

- Steam and cross-region pricing
- overseas / foreign-currency pricing
- actual RMB cost comparison
- region phrases such as 阿区、土区、日区、美区

This should reduce under-triggering.

### 2. Skill instructions now separate normalization from execution

The previous version implied that user inputs like `US$5.00` could be handled directly, while the script itself only accepted strict `currency amount` pairs.

The updated instructions now make the workflow explicit:

1. Normalize user-facing amounts into `currency amount`
2. Run `scripts/compare.py`
3. Summarize per-price best card and overall cheapest option

This keeps the skill behavior aligned with the script contract.

### 3. Script input parsing is more tolerant

The script has been upgraded to accept common user-style inputs rather than only strict two-token inputs.

Supported patterns now include:

- `usd 100`
- `100 usd`
- `US$5.99`
- `$9.99 USD`
- `JPY 1500`
- `1500 JPY`

This reduces friction and makes the skill more resilient when called by a model that has to interpret messy user text.

### 4. Error handling now distinguishes fetch failures from no-match results

Previously, network or parsing problems could collapse into a misleading "No match found" message.

The script now distinguishes:

- live fetch failure
- unsupported or unparseable input
- successful fetch but no matching hardcoded cards

This matters because the user should not interpret a transient upstream failure as a pricing result.

### 5. TLS handling was made safer

The previous script disabled certificate verification. That is risky for a tool whose output is financial decision support.

The updated version uses the default HTTPS verification path instead of bypassing TLS checks.

### 6. Output is more useful for multi-price comparisons

The original script mostly highlighted the global best option and showed a ranking only for that single winning entry.

The new output structure is clearer:

- each queried price gets its own best-card summary
- each queried price also shows its card ranking
- an overall cheapest option is still highlighted at the end

This makes the tool more useful for real region-to-region comparisons.

### 7. Card configuration is centralized

Card metadata is now structured more explicitly in code instead of relying on ad hoc string checks. This makes future edits safer if card names need to change.

### 8. Eval coverage was added

A new `evals/evals.json` file was added with realistic prompts covering:

- single-price queries
- mixed-format multi-price queries
- explicit anti-follow-up instructions
- Steam cross-region comparison language

This gives the skill a basic regression harness for future iterations.

### 9. JSON output mode was added

The script now supports a `--json` flag for machine-readable output.

This is useful when the skill needs to:

- summarize multiple queried prices reliably
- distinguish success from fetch or parse failures
- consume card rankings without depending on text formatting

The JSON payload includes:

- per-input status
- normalized currency and amount
- best card and best RMB cost
- card rankings
- overall best option across all successful inputs

### 10. Certificate fallback is now automatic and user-friendly

The script now tries standard HTTPS verification first.

If the current network environment fails certificate validation, it automatically retries in compatibility mode and includes a plain-language warning instead of surfacing raw TLS jargon to the end user.

This keeps the default behavior safety-first while still preserving usability in proxy-heavy or certificate-intercepted environments.

In practice, the warning shown to the user is now phrased in a more natural way:

- the site certificate could not be verified in the current network environment
- the result was fetched in compatibility mode
- the result is suitable for personal reference
- if the user wants extra confidence, they should recheck on another network

This is more usable than exposing phrases like "non-validated TLS chain" directly in the final answer.

### 11. More currencies are recognized directly by the parser

The parser now recognizes additional currencies that commonly appear in Steam cross-region pricing discussions, including:

- `SGD`
- `INR`

This closes a real gap found during live testing, where values like `46.19 SGD` and `3326.83 INR` should have been accepted but were initially rejected as input parse errors.

## Remaining Limitations

- The skill still depends on the HTML structure of `kylc.com`, so future upstream layout changes can still break parsing.
- Because the data source is live and external, local verification without network access can only validate syntax and control flow, not end-to-end correctness.
- Region labels such as 阿区 or 土区 are not directly interpreted by the script; they should remain explanatory labels around normalized currency inputs.
- The JSON schema is intentionally simple right now and is not yet versioned.
- Automatic certificate fallback improves usability, but it still means the result is better treated as personal-reference data when the warning appears.
- Additional currency aliases may still need to be added over time if future Steam pricing inputs involve more regions.

## Recommended Next Improvements

- Add fixture-based tests with saved HTML samples from `kylc.com`.
- Add assertions to eval metadata once expected response format is finalized.
- Consider exporting a machine-readable JSON mode for easier downstream summarization by the skill.
