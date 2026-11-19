# Capstone trials — after

- Server: https://fitfindr-am5n.onrender.com
- When: 2026-11-18 21:01
- Produced by: `trials.py::main`; records from `serve.py::ask` via GET /log

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Warm runs return a fit card in under 8 s | 4 of 5, 3 of 3 trials | FAIL 0/5 | FAIL 0/5 | FAIL 0/5 | MISSED |
| 2. A malformed request gets a 400 | 5 of 5, 3 of 3 trials | FAIL 2/5 | FAIL 2/5 | FAIL 2/5 | MISSED |
| 3. The log's time matches the wait when requests overlap | 2 of 2, 3 of 3 trials | PASS 2/2 | PASS 2/2 | PASS 2/2 | MET |
| 4. Every request leaves one matching record | all, 3 of 3 trials | PASS 13/13 | PASS 12/12 | PASS 12/12 | MET |
| 5. 2 model calls, mean cost ≤ $0.0008 | 5 of 5 and mean ≤ $0.0008, 3 of 3 trials | PASS 5/5, mean $0.000683 | PASS 5/5, mean $0.000680 | PASS 5/5, mean $0.000688 | MET |

## Trial 1

| Part | Request | Status | Client ms | X-Request-Id |
|---|---|---|---|---|
| warm-up | `{"query": "vintage graphic tee under $30"}` | 200 | 33012 | 5a0ff394 |
| c1 | `{"query": "90s track jacket in size M"}` | 200 | 23430 | e6c0ea56 |
| c1 | `{"query": "silk slip dress in midi length under $40"}` | 200 | 10577 | 1bc9071a |
| c1 | `{"query": "platform sneakers size 8"}` | 200 | 10254 | 52458348 |
| c1 | `{"query": "denim jacket under $50"}` | 200 | 17570 | 4dc745ae |
| c1 | `{"query": "chunky knit cardigan"}` | 200 | 18827 | a0da4a49 |
| c2 | `[1, 2]` | 500 | 147 | None |
| c2 | `{"query": 42}` | 500 | 119 | None |
| c2 | `"vintage tee"` | 500 | 147 | None |
| c2 | `{"query": ""}` | 400 | 131 | 9fc98a74 |
| c2 | `not json` | 400 | 117 | fe78293f |
| c3 | `{"query": "designer ballgown size XXS under $5"}` | 200 | 8182 | ac1e887e |
| c3 | `{"query": "wetsuit size XXS"}` | 200 | 16974 | 76dd6ad0 |

Log records after the mark:

```jsonl
{"ts": "2026-11-19T01:52:47.083+00:00", "request_id": "5a0ff394", "route": "/ask", "status": 200, "query": "vintage graphic tee under $30", "outcome": "fit_card", "item": "Vintage Band Tee — Faded Grey ($19.0, depop)", "error": null, "duration_ms": 32886, "waited_ms": 0, "model_calls": 2, "tokens_in": 717, "tokens_out": 177, "stages_ms": {"search_listings": 4250, "compare_price": 3998, "suggest_outfit": 15815, "create_fit_card": 8823}}
{"ts": "2026-11-19T01:53:20.161+00:00", "request_id": "e6c0ea56", "route": "/ask", "status": 200, "query": "90s track jacket in size M", "outcome": "fit_card", "item": "90s Track Jacket — Navy/White Stripe ($45.0, poshmark)", "error": null, "duration_ms": 23284, "waited_ms": 0, "model_calls": 2, "tokens_in": 721, "tokens_out": 162, "stages_ms": {"search_listings": 3769, "compare_price": 4100, "suggest_outfit": 8280, "create_fit_card": 7135}}
{"ts": "2026-11-19T01:53:43.602+00:00", "request_id": "1bc9071a", "route": "/ask", "status": 200, "query": "silk slip dress in midi length under $40", "outcome": "fit_card", "item": "90s Silk Slip Dress — Floral, Midi Length ($30.0, depop)", "error": null, "duration_ms": 10441, "waited_ms": 0, "model_calls": 2, "tokens_in": 760, "tokens_out": 210, "stages_ms": {"search_listings": 4531, "compare_price": 3904, "suggest_outfit": 1223, "create_fit_card": 783}}
{"ts": "2026-11-19T01:53:54.179+00:00", "request_id": "52458348", "route": "/ask", "status": 200, "query": "platform sneakers size 8", "outcome": "fit_card", "item": "Platform Sneakers — White Chunky Sole ($48.0, poshmark)", "error": null, "duration_ms": 10138, "waited_ms": 0, "model_calls": 2, "tokens_in": 736, "tokens_out": 199, "stages_ms": {"search_listings": 3861, "compare_price": 4388, "suggest_outfit": 953, "create_fit_card": 936}}
{"ts": "2026-11-19T01:54:04.462+00:00", "request_id": "4dc745ae", "route": "/ask", "status": 200, "query": "denim jacket under $50", "outcome": "fit_card", "item": "Denim Jacket — Light Wash, Cropped ($42.0, poshmark)", "error": null, "duration_ms": 17448, "waited_ms": 0, "model_calls": 2, "tokens_in": 708, "tokens_out": 163, "stages_ms": {"search_listings": 4067, "compare_price": 4697, "suggest_outfit": 911, "create_fit_card": 7773}}
{"ts": "2026-11-19T01:54:22.055+00:00", "request_id": "a0da4a49", "route": "/ask", "status": 200, "query": "chunky knit cardigan", "outcome": "fit_card", "item": "Knit Cardigan — Chunky Brown ($35.0, depop)", "error": null, "duration_ms": 18705, "waited_ms": 0, "model_calls": 2, "tokens_in": 740, "tokens_out": 193, "stages_ms": {"search_listings": 4377, "compare_price": 4198, "suggest_outfit": 1158, "create_fit_card": 8972}}
{"ts": "2026-11-19T01:54:40.931+00:00", "request_id": "c501d594", "route": "/ask", "status": 500, "query": "[1, 2]", "outcome": "crashed", "item": null, "error": "AttributeError: 'list' object has no attribute 'get'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T01:54:41.068+00:00", "request_id": "825a4596", "route": "/ask", "status": 500, "query": 42, "outcome": "crashed", "item": null, "error": "AttributeError: 'int' object has no attribute 'strip'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T01:54:41.235+00:00", "request_id": "8e8b8d5a", "route": "/ask", "status": 500, "query": "\"vintage tee\"", "outcome": "crashed", "item": null, "error": "AttributeError: 'str' object has no attribute 'get'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T01:54:41.393+00:00", "request_id": "9fc98a74", "route": "/ask", "status": 400, "query": "", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T01:54:41.527+00:00", "request_id": "fe78293f", "route": "/ask", "status": 400, "query": "not json", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T01:54:41.666+00:00", "request_id": "ac1e887e", "route": "/ask", "status": 200, "query": "designer ballgown size XXS under $5", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'designer ballgown' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, nothing is listed under $5 (the cheapest listing is $12), and no listing comes in size XXS.", "duration_ms": 8064, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 8061}}
{"ts": "2026-11-19T01:54:41.820+00:00", "request_id": "76dd6ad0", "route": "/ask", "status": 200, "query": "wetsuit size XXS", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'wetsuit' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, no listing comes in size XXS.", "duration_ms": 16705, "waited_ms": 7909, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 8793}}
```

## Trial 2

| Part | Request | Status | Client ms | X-Request-Id |
|---|---|---|---|---|
| c1 | `{"query": "90s track jacket in size M"}` | 200 | 24689 | 8a4fa7ef |
| c1 | `{"query": "silk slip dress in midi length under $40"}` | 200 | 16286 | a8cc1674 |
| c1 | `{"query": "platform sneakers size 8"}` | 200 | 24258 | 95d76410 |
| c1 | `{"query": "denim jacket under $50"}` | 200 | 16587 | d99c1a08 |
| c1 | `{"query": "chunky knit cardigan"}` | 200 | 19569 | 715fe18f |
| c2 | `[1, 2]` | 500 | 141 | None |
| c2 | `{"query": 42}` | 500 | 114 | None |
| c2 | `"vintage tee"` | 500 | 145 | None |
| c2 | `{"query": ""}` | 400 | 141 | 92bc14f0 |
| c2 | `not json` | 400 | 120 | f8c4be90 |
| c3 | `{"query": "designer ballgown size XXS under $5"}` | 200 | 16393 | 9dbf7567 |
| c3 | `{"query": "wetsuit size XXS"}` | 200 | 8476 | 0aab1c08 |

Log records after the mark:

```jsonl
{"ts": "2026-11-19T01:55:59.464+00:00", "request_id": "8a4fa7ef", "route": "/ask", "status": 200, "query": "90s track jacket in size M", "outcome": "fit_card", "item": "90s Track Jacket — Navy/White Stripe ($45.0, poshmark)", "error": null, "duration_ms": 24550, "waited_ms": 0, "model_calls": 2, "tokens_in": 725, "tokens_out": 173, "stages_ms": {"search_listings": 4055, "compare_price": 3912, "suggest_outfit": 8437, "create_fit_card": 8145}}
{"ts": "2026-11-19T01:56:24.393+00:00", "request_id": "a8cc1674", "route": "/ask", "status": 200, "query": "silk slip dress in midi length under $40", "outcome": "fit_card", "item": "90s Silk Slip Dress — Floral, Midi Length ($30.0, depop)", "error": null, "duration_ms": 15951, "waited_ms": 0, "model_calls": 2, "tokens_in": 783, "tokens_out": 222, "stages_ms": {"search_listings": 4037, "compare_price": 3989, "suggest_outfit": 1391, "create_fit_card": 6534}}
{"ts": "2026-11-19T01:56:40.496+00:00", "request_id": "95d76410", "route": "/ask", "status": 200, "query": "platform sneakers size 8", "outcome": "fit_card", "item": "Platform Sneakers — White Chunky Sole ($48.0, poshmark)", "error": null, "duration_ms": 24085, "waited_ms": 0, "model_calls": 2, "tokens_in": 703, "tokens_out": 146, "stages_ms": {"search_listings": 3830, "compare_price": 4203, "suggest_outfit": 8328, "create_fit_card": 7724}}
{"ts": "2026-11-19T01:57:04.795+00:00", "request_id": "d99c1a08", "route": "/ask", "status": 200, "query": "denim jacket under $50", "outcome": "fit_card", "item": "Denim Jacket — Light Wash, Cropped ($42.0, poshmark)", "error": null, "duration_ms": 16430, "waited_ms": 0, "model_calls": 2, "tokens_in": 739, "tokens_out": 205, "stages_ms": {"search_listings": 4234, "compare_price": 3899, "suggest_outfit": 7553, "create_fit_card": 743}}
{"ts": "2026-11-19T01:57:21.353+00:00", "request_id": "715fe18f", "route": "/ask", "status": 200, "query": "chunky knit cardigan", "outcome": "fit_card", "item": "Knit Cardigan — Chunky Brown ($35.0, depop)", "error": null, "duration_ms": 19456, "waited_ms": 0, "model_calls": 2, "tokens_in": 711, "tokens_out": 175, "stages_ms": {"search_listings": 3882, "compare_price": 4289, "suggest_outfit": 3153, "create_fit_card": 8131}}
{"ts": "2026-11-19T01:57:40.966+00:00", "request_id": "13790fdf", "route": "/ask", "status": 500, "query": "[1, 2]", "outcome": "crashed", "item": null, "error": "AttributeError: 'list' object has no attribute 'get'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T01:57:41.093+00:00", "request_id": "eed6c301", "route": "/ask", "status": 500, "query": 42, "outcome": "crashed", "item": null, "error": "AttributeError: 'int' object has no attribute 'strip'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T01:57:41.233+00:00", "request_id": "10e18b77", "route": "/ask", "status": 500, "query": "\"vintage tee\"", "outcome": "crashed", "item": null, "error": "AttributeError: 'str' object has no attribute 'get'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T01:57:41.401+00:00", "request_id": "92bc14f0", "route": "/ask", "status": 400, "query": "", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T01:57:41.531+00:00", "request_id": "f8c4be90", "route": "/ask", "status": 400, "query": "not json", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T01:57:41.656+00:00", "request_id": "0aab1c08", "route": "/ask", "status": 200, "query": "wetsuit size XXS", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'wetsuit' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, no listing comes in size XXS.", "duration_ms": 8364, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 8278}}
{"ts": "2026-11-19T01:57:41.661+00:00", "request_id": "9dbf7567", "route": "/ask", "status": 200, "query": "designer ballgown size XXS under $5", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'designer ballgown' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, nothing is listed under $5 (the cheapest listing is $12), and no listing comes in size XXS.", "duration_ms": 16271, "waited_ms": 8359, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 7910}}
```

## Trial 3

| Part | Request | Status | Client ms | X-Request-Id |
|---|---|---|---|---|
| c1 | `{"query": "90s track jacket in size M"}` | 200 | 18748 | 37d2cabd |
| c1 | `{"query": "silk slip dress in midi length under $40"}` | 200 | 14317 | e0c06f53 |
| c1 | `{"query": "platform sneakers size 8"}` | 200 | 17938 | 61beb321 |
| c1 | `{"query": "denim jacket under $50"}` | 200 | 27635 | df137276 |
| c1 | `{"query": "chunky knit cardigan"}` | 200 | 28297 | 4369df48 |
| c2 | `[1, 2]` | 500 | 123 | None |
| c2 | `{"query": 42}` | 500 | 138 | None |
| c2 | `"vintage tee"` | 500 | 151 | None |
| c2 | `{"query": ""}` | 400 | 268 | db85f319 |
| c2 | `not json` | 400 | 121 | 99d8c48c |
| c3 | `{"query": "designer ballgown size XXS under $5"}` | 200 | 17771 | 820dd2c0 |
| c3 | `{"query": "wetsuit size XXS"}` | 200 | 9262 | d7268185 |

Log records after the mark:

```jsonl
{"ts": "2026-11-19T01:58:58.890+00:00", "request_id": "37d2cabd", "route": "/ask", "status": 200, "query": "90s track jacket in size M", "outcome": "fit_card", "item": "90s Track Jacket — Navy/White Stripe ($45.0, poshmark)", "error": null, "duration_ms": 18605, "waited_ms": 0, "model_calls": 2, "tokens_in": 725, "tokens_out": 181, "stages_ms": {"search_listings": 4339, "compare_price": 4099, "suggest_outfit": 9076, "create_fit_card": 1089}}
{"ts": "2026-11-19T01:59:17.642+00:00", "request_id": "e0c06f53", "route": "/ask", "status": 200, "query": "silk slip dress in midi length under $40", "outcome": "fit_card", "item": "90s Silk Slip Dress — Floral, Midi Length ($30.0, depop)", "error": null, "duration_ms": 14027, "waited_ms": 0, "model_calls": 2, "tokens_in": 761, "tokens_out": 208, "stages_ms": {"search_listings": 3697, "compare_price": 4290, "suggest_outfit": 5329, "create_fit_card": 711}}
{"ts": "2026-11-19T01:59:32.311+00:00", "request_id": "61beb321", "route": "/ask", "status": 200, "query": "platform sneakers size 8", "outcome": "fit_card", "item": "Platform Sneakers — White Chunky Sole ($48.0, poshmark)", "error": null, "duration_ms": 17492, "waited_ms": 0, "model_calls": 2, "tokens_in": 705, "tokens_out": 163, "stages_ms": {"search_listings": 4316, "compare_price": 4208, "suggest_outfit": 7994, "create_fit_card": 974}}
{"ts": "2026-11-19T01:59:49.968+00:00", "request_id": "df137276", "route": "/ask", "status": 200, "query": "denim jacket under $50", "outcome": "fit_card", "item": "Denim Jacket — Light Wash, Cropped ($42.0, poshmark)", "error": null, "duration_ms": 27487, "waited_ms": 0, "model_calls": 2, "tokens_in": 720, "tokens_out": 186, "stages_ms": {"search_listings": 4258, "compare_price": 4009, "suggest_outfit": 9585, "create_fit_card": 9634}}
{"ts": "2026-11-19T02:00:17.628+00:00", "request_id": "4369df48", "route": "/ask", "status": 200, "query": "chunky knit cardigan", "outcome": "fit_card", "item": "Knit Cardigan — Chunky Brown ($35.0, depop)", "error": null, "duration_ms": 28161, "waited_ms": 0, "model_calls": 2, "tokens_in": 749, "tokens_out": 198, "stages_ms": {"search_listings": 4009, "compare_price": 3982, "suggest_outfit": 16357, "create_fit_card": 3812}}
{"ts": "2026-11-19T02:00:45.935+00:00", "request_id": "1ab6d5ec", "route": "/ask", "status": 500, "query": "[1, 2]", "outcome": "crashed", "item": null, "error": "AttributeError: 'list' object has no attribute 'get'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T02:00:46.102+00:00", "request_id": "977672fc", "route": "/ask", "status": 500, "query": 42, "outcome": "crashed", "item": null, "error": "AttributeError: 'int' object has no attribute 'strip'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T02:00:46.279+00:00", "request_id": "be92ca01", "route": "/ask", "status": 500, "query": "\"vintage tee\"", "outcome": "crashed", "item": null, "error": "AttributeError: 'str' object has no attribute 'get'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T02:00:46.578+00:00", "request_id": "db85f319", "route": "/ask", "status": 400, "query": "", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T02:00:46.719+00:00", "request_id": "99d8c48c", "route": "/ask", "status": 400, "query": "not json", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T02:00:46.901+00:00", "request_id": "d7268185", "route": "/ask", "status": 200, "query": "wetsuit size XXS", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'wetsuit' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, no listing comes in size XXS.", "duration_ms": 9120, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 9037}}
{"ts": "2026-11-19T02:00:46.905+00:00", "request_id": "820dd2c0", "route": "/ask", "status": 200, "query": "designer ballgown size XXS under $5", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'designer ballgown' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, nothing is listed under $5 (the cheapest listing is $12), and no listing comes in size XXS.", "duration_ms": 17623, "waited_ms": 9115, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 8506}}
```
