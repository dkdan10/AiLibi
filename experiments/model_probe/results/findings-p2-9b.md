# Model-probe findings — p2-9b

## Per-cell metrics (model × think × num_ctx × variant)

| model | think | num_ctx | variant | calls | parse_ok_rate | n_avail | conversion_avail | n_noavail | false_eject_noavail | skip_rate_of_parsed | mean_rationale_chars | mean_latency_s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen3.5:9b | False | 8192 | baseline | 81 | 1.0 | 26 | 0.038 | 55 | 0.0 | 0.988 | 425.9 | 15.9 |
| qwen3.5:9b | False | 8192 | v1_verdict | 81 | 1.0 | 26 | 0.769 | 55 | 0.0 | 0.753 | 336.6 | 14.4 |

## Attribution (recorded skips: prompt- vs config- vs model-fixable)

```json
{
  "inversion_items": 18,
  "prompt_fixable": [
    "2:headless-seed-2:meeting-0:p-3",
    "2:headless-seed-2:meeting-0:p-8",
    "2:headless-seed-2:meeting-0:p-9",
    "2:headless-seed-2:meeting-1:p-1",
    "2:headless-seed-2:meeting-1:p-8",
    "2:headless-seed-2:meeting-2:p-8",
    "5:headless-seed-5:meeting-0:p-7",
    "8:headless-seed-8:meeting-1:p-1",
    "8:headless-seed-8:meeting-1:p-2",
    "8:headless-seed-8:meeting-1:p-7",
    "8:headless-seed-8:meeting-1:p-9",
    "9:headless-seed-9:meeting-0:p-1"
  ],
  "config_fixable": [],
  "model_bound": [
    "2:headless-seed-2:meeting-1:p-9",
    "3:headless-seed-3:meeting-0:p-5",
    "3:headless-seed-3:meeting-0:p-7",
    "9:headless-seed-9:meeting-0:p-9",
    "9:headless-seed-9:meeting-1:p-1",
    "9:headless-seed-9:meeting-1:p-9"
  ]
}
```