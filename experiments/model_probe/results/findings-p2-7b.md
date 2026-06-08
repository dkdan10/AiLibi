# Model-probe findings — p2-7b

## Per-cell metrics (model × think × num_ctx × variant)

| model | think | num_ctx | variant | calls | parse_ok_rate | n_avail | conversion_avail | n_noavail | false_eject_noavail | skip_rate_of_parsed | mean_rationale_chars | mean_latency_s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5:7b-instruct | False | 8192 | baseline | 81 | 1.0 | 26 | 0.346 | 55 | 0.0 | 0.889 | 147.8 | 11.3 |
| qwen2.5:7b-instruct | False | 8192 | v1_verdict | 81 | 1.0 | 26 | 1.0 | 55 | 0.0 | 0.679 | 136.9 | 10.7 |
| qwen2.5:7b-instruct | False | 8192 | v2_symmetric | 81 | 1.0 | 26 | 0.808 | 55 | 0.164 | 0.63 | 126.5 | 11.3 |
| qwen2.5:7b-instruct | False | 8192 | v4_brief | 81 | 1.0 | 26 | 0.962 | 55 | 0.2 | 0.556 | 45.7 | 9.6 |

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
    "2:headless-seed-2:meeting-1:p-9",
    "2:headless-seed-2:meeting-2:p-8",
    "3:headless-seed-3:meeting-0:p-5",
    "3:headless-seed-3:meeting-0:p-7",
    "5:headless-seed-5:meeting-0:p-7",
    "8:headless-seed-8:meeting-1:p-1",
    "8:headless-seed-8:meeting-1:p-2",
    "8:headless-seed-8:meeting-1:p-7",
    "8:headless-seed-8:meeting-1:p-9",
    "9:headless-seed-9:meeting-0:p-1",
    "9:headless-seed-9:meeting-0:p-9",
    "9:headless-seed-9:meeting-1:p-1",
    "9:headless-seed-9:meeting-1:p-9"
  ],
  "config_fixable": [],
  "model_bound": []
}
```