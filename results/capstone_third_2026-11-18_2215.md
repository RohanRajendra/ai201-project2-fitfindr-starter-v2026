# Capstone trials — third

- Server: https://fitfindr-am5n.onrender.com
- When: 2026-11-18 22:15
- Produced by: `trials.py::main`; records from `serve.py::ask` via GET /log

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Warm runs return a fit card in under 8 s | 4 of 5, 3 of 3 trials | FAIL 0/5 | FAIL 0/5 | FAIL 0/5 | MISSED |
| 2. A malformed request gets a 400 | 5 of 5, 3 of 3 trials | PASS 5/5 | PASS 5/5 | PASS 5/5 | MET |
| 3. The log's time matches the wait when requests overlap | 2 of 2, 3 of 3 trials | PASS 2/2 | PASS 2/2 | PASS 2/2 | MET |
| 4. Every request leaves one matching record | all, 3 of 3 trials | PASS 13/13 | PASS 12/12 | PASS 12/12 | MET |
| 5. 2 model calls, mean cost ≤ $0.0008 | 5 of 5 and mean ≤ $0.0008, 3 of 3 trials | PASS 5/5, mean $0.000673 | PASS 5/5, mean $0.000662 | PASS 5/5, mean $0.000695 | MET |

## Trial 1

| Part | Request | Status | Client ms | X-Request-Id |
|---|---|---|---|---|
| warm-up | `{"query": "vintage graphic tee under $30"}` | 200 | 21324 | 8f7f8eb1 |
| c1 | `{"query": "90s track jacket in size M"}` | 200 | 13561 | d9a3163a |
| c1 | `{"query": "silk slip dress in midi length under $40"}` | 200 | 10451 | 452429d4 |
| c1 | `{"query": "platform sneakers size 8"}` | 200 | 9785 | acc057cb |
| c1 | `{"query": "denim jacket under $50"}` | 200 | 10148 | aee22bf0 |
| c1 | `{"query": "chunky knit cardigan"}` | 200 | 9682 | 014be971 |
| c2 | `[1, 2]` | 400 | 137 | a3d5bc3e |
| c2 | `{"query": 42}` | 400 | 111 | c6d409fc |
| c2 | `"vintage tee"` | 400 | 136 | 1dff0a95 |
| c2 | `{"query": ""}` | 400 | 133 | f01aefb4 |
| c2 | `not json` | 400 | 108 | d9267fd7 |
| c3 | `{"query": "designer ballgown size XXS under $5"}` | 200 | 8153 | 729bccb9 |
| c3 | `{"query": "wetsuit size XXS"}` | 200 | 16052 | b5f0cef3 |

Log records after the mark:

```jsonl
{"ts": "2026-11-19T03:09:50.440+00:00", "request_id": "8f7f8eb1", "route": "/ask", "status": 200, "query": "vintage graphic tee under $30", "outcome": "fit_card", "item": "Vintage Band Tee — Faded Grey ($19.0, depop)", "error": null, "duration_ms": 21203, "waited_ms": 0, "model_calls": 2, "tokens_in": 732, "tokens_out": 183, "stages_ms": {"search_listings": 9185, "compare_price": 4304, "suggest_outfit": 6712, "create_fit_card": 1001}}
{"ts": "2026-11-19T03:10:11.805+00:00", "request_id": "d9a3163a", "route": "/ask", "status": 200, "query": "90s track jacket in size M", "outcome": "fit_card", "item": "90s Track Jacket — Navy/White Stripe ($45.0, poshmark)", "error": null, "duration_ms": 13423, "waited_ms": 0, "model_calls": 2, "tokens_in": 722, "tokens_out": 186, "stages_ms": {"search_listings": 4224, "compare_price": 4204, "suggest_outfit": 2454, "create_fit_card": 2540}}
{"ts": "2026-11-19T03:10:25.509+00:00", "request_id": "452429d4", "route": "/ask", "status": 200, "query": "silk slip dress in midi length under $40", "outcome": "fit_card", "item": "90s Silk Slip Dress — Floral, Midi Length ($30.0, depop)", "error": null, "duration_ms": 10203, "waited_ms": 0, "model_calls": 2, "tokens_in": 735, "tokens_out": 183, "stages_ms": {"search_listings": 4016, "compare_price": 4205, "suggest_outfit": 1172, "create_fit_card": 809}}
{"ts": "2026-11-19T03:10:35.850+00:00", "request_id": "acc057cb", "route": "/ask", "status": 200, "query": "platform sneakers size 8", "outcome": "fit_card", "item": "Platform Sneakers — White Chunky Sole ($48.0, poshmark)", "error": null, "duration_ms": 9674, "waited_ms": 0, "model_calls": 2, "tokens_in": 710, "tokens_out": 170, "stages_ms": {"search_listings": 3981, "compare_price": 3997, "suggest_outfit": 898, "create_fit_card": 798}}
{"ts": "2026-11-19T03:10:45.659+00:00", "request_id": "aee22bf0", "route": "/ask", "status": 200, "query": "denim jacket under $50", "outcome": "fit_card", "item": "Denim Jacket — Light Wash, Cropped ($42.0, poshmark)", "error": null, "duration_ms": 10034, "waited_ms": 0, "model_calls": 2, "tokens_in": 731, "tokens_out": 200, "stages_ms": {"search_listings": 3865, "compare_price": 3803, "suggest_outfit": 1123, "create_fit_card": 1243}}
{"ts": "2026-11-19T03:10:55.861+00:00", "request_id": "014be971", "route": "/ask", "status": 200, "query": "chunky knit cardigan", "outcome": "fit_card", "item": "Knit Cardigan — Chunky Brown ($35.0, depop)", "error": null, "duration_ms": 9534, "waited_ms": 0, "model_calls": 2, "tokens_in": 725, "tokens_out": 173, "stages_ms": {"search_listings": 3682, "compare_price": 4293, "suggest_outfit": 957, "create_fit_card": 601}}
{"ts": "2026-11-19T03:11:05.563+00:00", "request_id": "a3d5bc3e", "route": "/ask", "status": 400, "query": "[1, 2]", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T03:11:05.710+00:00", "request_id": "c6d409fc", "route": "/ask", "status": 400, "query": 42, "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T03:11:05.868+00:00", "request_id": "1dff0a95", "route": "/ask", "status": 400, "query": "\"vintage tee\"", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T03:11:06.024+00:00", "request_id": "f01aefb4", "route": "/ask", "status": 400, "query": "", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T03:11:06.154+00:00", "request_id": "d9267fd7", "route": "/ask", "status": 400, "query": "not json", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T03:11:06.287+00:00", "request_id": "729bccb9", "route": "/ask", "status": 200, "query": "designer ballgown size XXS under $5", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'designer ballgown' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, nothing is listed under $5 (the cheapest listing is $12), and no listing comes in size XXS.", "duration_ms": 8041, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 8038}}
{"ts": "2026-11-19T03:11:06.294+00:00", "request_id": "b5f0cef3", "route": "/ask", "status": 200, "query": "wetsuit size XXS", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'wetsuit' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, no listing comes in size XXS.", "duration_ms": 15932, "waited_ms": 8034, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 7896}}
```

## Trial 2

| Part | Request | Status | Client ms | X-Request-Id |
|---|---|---|---|---|
| c1 | `{"query": "90s track jacket in size M"}` | 200 | 10049 | d7756fa8 |
| c1 | `{"query": "silk slip dress in midi length under $40"}` | 200 | 9787 | 9bdd993e |
| c1 | `{"query": "platform sneakers size 8"}` | 200 | 10295 | 50200f51 |
| c1 | `{"query": "denim jacket under $50"}` | 200 | 9739 | e93cb36f |
| c1 | `{"query": "chunky knit cardigan"}` | 200 | 10332 | 50a5ca66 |
| c2 | `[1, 2]` | 400 | 130 | e999055a |
| c2 | `{"query": 42}` | 400 | 111 | 0da312b5 |
| c2 | `"vintage tee"` | 400 | 131 | eb5b0667 |
| c2 | `{"query": ""}` | 400 | 133 | a7f5018d |
| c2 | `not json` | 400 | 149 | a495b8df |
| c3 | `{"query": "designer ballgown size XXS under $5"}` | 200 | 8279 | adbad3fc |
| c3 | `{"query": "wetsuit size XXS"}` | 200 | 16375 | a429ea2b |

Log records after the mark:

```jsonl
{"ts": "2026-11-19T03:12:23.104+00:00", "request_id": "d7756fa8", "route": "/ask", "status": 200, "query": "90s track jacket in size M", "outcome": "fit_card", "item": "90s Track Jacket — Navy/White Stripe ($45.0, poshmark)", "error": null, "duration_ms": 9918, "waited_ms": 0, "model_calls": 2, "tokens_in": 730, "tokens_out": 178, "stages_ms": {"search_listings": 3935, "compare_price": 3998, "suggest_outfit": 1037, "create_fit_card": 948}}
{"ts": "2026-11-19T03:12:33.177+00:00", "request_id": "9bdd993e", "route": "/ask", "status": 200, "query": "silk slip dress in midi length under $40", "outcome": "fit_card", "item": "90s Silk Slip Dress — Floral, Midi Length ($30.0, depop)", "error": null, "duration_ms": 9650, "waited_ms": 0, "model_calls": 2, "tokens_in": 754, "tokens_out": 194, "stages_ms": {"search_listings": 4248, "compare_price": 3903, "suggest_outfit": 854, "create_fit_card": 644}}
{"ts": "2026-11-19T03:12:42.990+00:00", "request_id": "50200f51", "route": "/ask", "status": 200, "query": "platform sneakers size 8", "outcome": "fit_card", "item": "Platform Sneakers — White Chunky Sole ($48.0, poshmark)", "error": null, "duration_ms": 10153, "waited_ms": 0, "model_calls": 2, "tokens_in": 715, "tokens_out": 169, "stages_ms": {"search_listings": 3834, "compare_price": 4304, "suggest_outfit": 1169, "create_fit_card": 845}}
{"ts": "2026-11-19T03:12:53.290+00:00", "request_id": "e93cb36f", "route": "/ask", "status": 200, "query": "denim jacket under $50", "outcome": "fit_card", "item": "Denim Jacket — Light Wash, Cropped ($42.0, poshmark)", "error": null, "duration_ms": 9614, "waited_ms": 0, "model_calls": 2, "tokens_in": 708, "tokens_out": 171, "stages_ms": {"search_listings": 3935, "compare_price": 4099, "suggest_outfit": 756, "create_fit_card": 823}}
{"ts": "2026-11-19T03:13:03.106+00:00", "request_id": "50a5ca66", "route": "/ask", "status": 200, "query": "chunky knit cardigan", "outcome": "fit_card", "item": "Knit Cardigan — Chunky Brown ($35.0, depop)", "error": null, "duration_ms": 10155, "waited_ms": 0, "model_calls": 2, "tokens_in": 726, "tokens_out": 177, "stages_ms": {"search_listings": 4220, "compare_price": 4098, "suggest_outfit": 1188, "create_fit_card": 648}}
{"ts": "2026-11-19T03:13:13.421+00:00", "request_id": "e999055a", "route": "/ask", "status": 400, "query": "[1, 2]", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T03:13:13.554+00:00", "request_id": "0da312b5", "route": "/ask", "status": 400, "query": 42, "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T03:13:13.706+00:00", "request_id": "eb5b0667", "route": "/ask", "status": 400, "query": "\"vintage tee\"", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T03:13:13.861+00:00", "request_id": "a7f5018d", "route": "/ask", "status": 400, "query": "", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T03:13:14.033+00:00", "request_id": "a495b8df", "route": "/ask", "status": 400, "query": "not json", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T03:13:14.169+00:00", "request_id": "adbad3fc", "route": "/ask", "status": 200, "query": "designer ballgown size XXS under $5", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'designer ballgown' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, nothing is listed under $5 (the cheapest listing is $12), and no listing comes in size XXS.", "duration_ms": 8163, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 8162}}
{"ts": "2026-11-19T03:13:14.184+00:00", "request_id": "a429ea2b", "route": "/ask", "status": 200, "query": "wetsuit size XXS", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'wetsuit' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, no listing comes in size XXS.", "duration_ms": 16244, "waited_ms": 8147, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 8095}}
```

## Trial 3

| Part | Request | Status | Client ms | X-Request-Id |
|---|---|---|---|---|
| c1 | `{"query": "90s track jacket in size M"}` | 200 | 9333 | 99cdb8a4 |
| c1 | `{"query": "silk slip dress in midi length under $40"}` | 200 | 10261 | ea748f99 |
| c1 | `{"query": "platform sneakers size 8"}` | 200 | 10398 | 9af0cd03 |
| c1 | `{"query": "denim jacket under $50"}` | 200 | 10353 | 81fb1d8c |
| c1 | `{"query": "chunky knit cardigan"}` | 200 | 10570 | 666176bf |
| c2 | `[1, 2]` | 400 | 144 | eb6d2def |
| c2 | `{"query": 42}` | 400 | 141 | 8f5333fd |
| c2 | `"vintage tee"` | 400 | 131 | 78bf6f5f |
| c2 | `{"query": ""}` | 400 | 135 | 9e6f116a |
| c2 | `not json` | 400 | 134 | 48fb58d7 |
| c3 | `{"query": "designer ballgown size XXS under $5"}` | 200 | 17780 | 5dfdd41a |
| c3 | `{"query": "wetsuit size XXS"}` | 200 | 8871 | 1fc11921 |

Log records after the mark:

```jsonl
{"ts": "2026-11-19T03:14:31.256+00:00", "request_id": "99cdb8a4", "route": "/ask", "status": 200, "query": "90s track jacket in size M", "outcome": "fit_card", "item": "90s Track Jacket — Navy/White Stripe ($45.0, poshmark)", "error": null, "duration_ms": 9195, "waited_ms": 0, "model_calls": 2, "tokens_in": 725, "tokens_out": 175, "stages_ms": {"search_listings": 3772, "compare_price": 3697, "suggest_outfit": 913, "create_fit_card": 813}}
{"ts": "2026-11-19T03:14:40.740+00:00", "request_id": "ea748f99", "route": "/ask", "status": 200, "query": "silk slip dress in midi length under $40", "outcome": "fit_card", "item": "90s Silk Slip Dress — Floral, Midi Length ($30.0, depop)", "error": null, "duration_ms": 9983, "waited_ms": 0, "model_calls": 2, "tokens_in": 759, "tokens_out": 198, "stages_ms": {"search_listings": 4192, "compare_price": 3990, "suggest_outfit": 957, "create_fit_card": 843}}
{"ts": "2026-11-19T03:14:50.897+00:00", "request_id": "9af0cd03", "route": "/ask", "status": 200, "query": "platform sneakers size 8", "outcome": "fit_card", "item": "Platform Sneakers — White Chunky Sole ($48.0, poshmark)", "error": null, "duration_ms": 10255, "waited_ms": 0, "model_calls": 2, "tokens_in": 733, "tokens_out": 183, "stages_ms": {"search_listings": 4033, "compare_price": 4192, "suggest_outfit": 931, "create_fit_card": 1098}}
{"ts": "2026-11-19T03:15:01.316+00:00", "request_id": "81fb1d8c", "route": "/ask", "status": 200, "query": "denim jacket under $50", "outcome": "fit_card", "item": "Denim Jacket — Light Wash, Cropped ($42.0, poshmark)", "error": null, "duration_ms": 10214, "waited_ms": 0, "model_calls": 2, "tokens_in": 749, "tokens_out": 210, "stages_ms": {"search_listings": 4104, "compare_price": 4297, "suggest_outfit": 1008, "create_fit_card": 791}}
{"ts": "2026-11-19T03:15:11.696+00:00", "request_id": "666176bf", "route": "/ask", "status": 200, "query": "chunky knit cardigan", "outcome": "fit_card", "item": "Knit Cardigan — Chunky Brown ($35.0, depop)", "error": null, "duration_ms": 10432, "waited_ms": 0, "model_calls": 2, "tokens_in": 733, "tokens_out": 180, "stages_ms": {"search_listings": 3942, "compare_price": 4489, "suggest_outfit": 1208, "create_fit_card": 792}}
{"ts": "2026-11-19T03:15:22.300+00:00", "request_id": "eb6d2def", "route": "/ask", "status": 400, "query": "[1, 2]", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T03:15:22.466+00:00", "request_id": "8f5333fd", "route": "/ask", "status": 400, "query": 42, "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T03:15:22.615+00:00", "request_id": "78bf6f5f", "route": "/ask", "status": 400, "query": "\"vintage tee\"", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T03:15:22.776+00:00", "request_id": "9e6f116a", "route": "/ask", "status": 400, "query": "", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T03:15:22.930+00:00", "request_id": "48fb58d7", "route": "/ask", "status": 400, "query": "not json", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T03:15:23.095+00:00", "request_id": "1fc11921", "route": "/ask", "status": 200, "query": "wetsuit size XXS", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'wetsuit' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, no listing comes in size XXS.", "duration_ms": 8731, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 8728}}
{"ts": "2026-11-19T03:15:23.107+00:00", "request_id": "5dfdd41a", "route": "/ask", "status": 200, "query": "designer ballgown size XXS under $5", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'designer ballgown' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, nothing is listed under $5 (the cheapest listing is $12), and no listing comes in size XXS.", "duration_ms": 17629, "waited_ms": 8718, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 8909}}
```
