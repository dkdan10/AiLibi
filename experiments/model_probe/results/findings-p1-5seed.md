# Model-probe findings — p1-5seed

## Per-cell metrics (model × think × num_ctx × variant)

| model | think | num_ctx | variant | calls | parse_ok_rate | conversion_of_all | skip_rate_of_parsed | mean_latency_s | mean_out_tokens | mean_rationale_chars | max_rationale_chars | mean_thinking_chars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5:7b-instruct | False | 8192 | baseline | 13 | 1.0 | 0.462 | 0.538 | 12.5 | 85.2 | 148.8 | 260 | 0.0 |
| qwen2.5:7b-instruct | False | 16384 | baseline | 13 | 1.0 | 0.462 | 0.538 | 12.5 | 85.2 | 148.8 | 260 | 0.0 |
| qwen2.5:7b-instruct | True | 8192 | baseline | 13 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0 | 0.0 |
| qwen2.5:7b-instruct | True | 16384 | baseline | 13 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0 | 0.0 |
| qwen3.5:9b | False | 8192 | baseline | 13 | 1.0 | 0.0 | 1.0 | 18.3 | 154.4 | 464.6 | 570 | 0.0 |
| qwen3.5:9b | False | 16384 | baseline | 13 | 1.0 | 0.0 | 1.0 | 18.1 | 154.4 | 464.6 | 570 | 0.0 |
| qwen3.5:9b | True | 8192 | baseline | 13 | 0.0 | 0.0 | 0.0 | 16.2 | 118.2 | 0.0 | 0 | 447.9 |
| qwen3.5:9b | True | 16384 | baseline | 13 | 0.0 | 0.0 | 0.0 | 16.3 | 118.2 | 0.0 | 0 | 447.9 |

## Attribution (recorded skips: prompt- vs config- vs model-fixable)

```json
{
  "note": "single variant (baseline) \u2014 run >1 variant for attribution"
}
```