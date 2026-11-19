# Capstone trials — before

- Server: https://fitfindr-am5n.onrender.com
- When: 2026-11-18 19:40
- Produced by: `trials.py::main`; records from `serve.py::ask` via GET /log

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Warm runs return a fit card in under 8 s | 4 of 5, 3 of 3 trials | FAIL 0/5 | FAIL 0/5 | FAIL 0/5 | MISSED |
| 2. A malformed request gets a 400 | 5 of 5, 3 of 3 trials | FAIL 2/5 | FAIL 2/5 | FAIL 2/5 | MISSED |
| 3. The log's time matches the wait when requests overlap | 2 of 2, 3 of 3 trials | FAIL 1/2 | FAIL 1/2 | FAIL 1/2 | MISSED |
| 4. Every request leaves one matching record | all, 3 of 3 trials | PASS 13/13 | PASS 12/12 | PASS 12/12 | MET |
| 5. 2 model calls, mean cost ≤ $0.0008 | 5 of 5 and mean ≤ $0.0008, 3 of 3 trials | PASS 5/5, mean $0.000630 | PASS 5/5, mean $0.000671 | PASS 5/5, mean $0.000665 | MET |

## Trial 1

| Part | Request | Status | Client ms | X-Request-Id |
|---|---|---|---|---|
| warm-up | `{"query": "vintage graphic tee under $30"}` | 200 | 20039 | df28cbc6 |
| c1 | `{"query": "90s track jacket in size M"}` | 200 | 9820 | dd7b3ff9 |
| c1 | `{"query": "silk slip dress in midi length under $40"}` | 200 | 9812 | 6d686e06 |
| c1 | `{"query": "platform sneakers size 8"}` | 200 | 9545 | a202e3f1 |
| c1 | `{"query": "denim jacket under $50"}` | 200 | 10440 | a18c6bf3 |
| c1 | `{"query": "chunky knit cardigan"}` | 200 | 9945 | 64cf0931 |
| c2 | `[1, 2]` | 500 | 133 | None |
| c2 | `{"query": 42}` | 500 | 136 | None |
| c2 | `"vintage tee"` | 500 | 327 | None |
| c2 | `{"query": ""}` | 400 | 118 | 682c6255 |
| c2 | `not json` | 400 | 138 | c3690903 |
| c3 | `{"query": "designer ballgown size XXS under $5"}` | 200 | 8098 | 22047c7b |
| c3 | `{"query": "wetsuit size XXS"}` | 200 | 15679 | 4080b34d |

Log records after the mark:

```jsonl
{"ts": "2026-11-19T00:34:40.412+00:00", "request_id": "df28cbc6", "route": "/ask", "status": 200, "query": "vintage graphic tee under $30", "outcome": "fit_card", "item": "Vintage Band Tee — Faded Grey ($19.0, depop)", "error": null, "duration_ms": 19897, "waited_ms": 0, "model_calls": 2, "tokens_in": 713, "tokens_out": 181, "stages_ms": {"search_listings": 8148, "compare_price": 3693, "suggest_outfit": 7191, "create_fit_card": 863}}
{"ts": "2026-11-19T00:35:00.473+00:00", "request_id": "dd7b3ff9", "route": "/ask", "status": 200, "query": "90s track jacket in size M", "outcome": "fit_card", "item": "90s Track Jacket — Navy/White Stripe ($45.0, poshmark)", "error": null, "duration_ms": 9681, "waited_ms": 0, "model_calls": 2, "tokens_in": 725, "tokens_out": 168, "stages_ms": {"search_listings": 3983, "compare_price": 3788, "suggest_outfit": 1152, "create_fit_card": 757}}
{"ts": "2026-11-19T00:35:10.331+00:00", "request_id": "6d686e06", "route": "/ask", "status": 200, "query": "silk slip dress in midi length under $40", "outcome": "fit_card", "item": "90s Silk Slip Dress — Floral, Midi Length ($30.0, depop)", "error": null, "duration_ms": 9659, "waited_ms": 0, "model_calls": 2, "tokens_in": 731, "tokens_out": 189, "stages_ms": {"search_listings": 3922, "compare_price": 4097, "suggest_outfit": 758, "create_fit_card": 881}}
{"ts": "2026-11-19T00:35:20.290+00:00", "request_id": "a202e3f1", "route": "/ask", "status": 200, "query": "platform sneakers size 8", "outcome": "fit_card", "item": "Platform Sneakers — White Chunky Sole ($48.0, poshmark)", "error": null, "duration_ms": 9330, "waited_ms": 0, "model_calls": 2, "tokens_in": 700, "tokens_out": 143, "stages_ms": {"search_listings": 3774, "compare_price": 3996, "suggest_outfit": 894, "create_fit_card": 665}}
{"ts": "2026-11-19T00:35:29.773+00:00", "request_id": "a18c6bf3", "route": "/ask", "status": 200, "query": "denim jacket under $50", "outcome": "fit_card", "item": "Denim Jacket — Light Wash, Cropped ($42.0, poshmark)", "error": null, "duration_ms": 10319, "waited_ms": 0, "model_calls": 2, "tokens_in": 689, "tokens_out": 150, "stages_ms": {"search_listings": 4484, "compare_price": 3996, "suggest_outfit": 1167, "create_fit_card": 672}}
{"ts": "2026-11-19T00:35:40.277+00:00", "request_id": "64cf0931", "route": "/ask", "status": 200, "query": "chunky knit cardigan", "outcome": "fit_card", "item": "Knit Cardigan — Chunky Brown ($35.0, depop)", "error": null, "duration_ms": 9784, "waited_ms": 0, "model_calls": 2, "tokens_in": 728, "tokens_out": 181, "stages_ms": {"search_listings": 3774, "compare_price": 3807, "suggest_outfit": 1319, "create_fit_card": 884}}
{"ts": "2026-11-19T00:35:50.220+00:00", "request_id": "88462679", "route": "/ask", "status": 500, "query": "[1, 2]", "outcome": "crashed", "item": null, "error": "AttributeError: 'list' object has no attribute 'get'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T00:35:50.381+00:00", "request_id": "9b28f994", "route": "/ask", "status": 500, "query": 42, "outcome": "crashed", "item": null, "error": "AttributeError: 'int' object has no attribute 'strip'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T00:35:50.731+00:00", "request_id": "f3040b80", "route": "/ask", "status": 500, "query": "\"vintage tee\"", "outcome": "crashed", "item": null, "error": "AttributeError: 'str' object has no attribute 'get'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T00:35:50.871+00:00", "request_id": "682c6255", "route": "/ask", "status": 400, "query": "", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T00:35:51.038+00:00", "request_id": "c3690903", "route": "/ask", "status": 400, "query": "not json", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T00:35:51.181+00:00", "request_id": "22047c7b", "route": "/ask", "status": 200, "query": "designer ballgown size XXS under $5", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'designer ballgown' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, nothing is listed under $5 (the cheapest listing is $12), and no listing comes in size XXS.", "duration_ms": 7977, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 7974}}
{"ts": "2026-11-19T00:35:59.159+00:00", "request_id": "4080b34d", "route": "/ask", "status": 200, "query": "wetsuit size XXS", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'wetsuit' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, no listing comes in size XXS.", "duration_ms": 7588, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 7498}}
```

## Trial 2

| Part | Request | Status | Client ms | X-Request-Id |
|---|---|---|---|---|
| c1 | `{"query": "90s track jacket in size M"}` | 200 | 10037 | 92cf28fb |
| c1 | `{"query": "silk slip dress in midi length under $40"}` | 200 | 9697 | 3930af13 |
| c1 | `{"query": "platform sneakers size 8"}` | 200 | 9205 | b43d8366 |
| c1 | `{"query": "denim jacket under $50"}` | 200 | 9181 | 43023003 |
| c1 | `{"query": "chunky knit cardigan"}` | 200 | 9582 | 7d0b5f6f |
| c2 | `[1, 2]` | 500 | 139 | None |
| c2 | `{"query": 42}` | 500 | 135 | None |
| c2 | `"vintage tee"` | 500 | 151 | None |
| c2 | `{"query": ""}` | 400 | 130 | babc3583 |
| c2 | `not json` | 400 | 133 | 4c315806 |
| c3 | `{"query": "designer ballgown size XXS under $5"}` | 200 | 7373 | bea74bf1 |
| c3 | `{"query": "wetsuit size XXS"}` | 200 | 15287 | 8b771a91 |

Log records after the mark:

```jsonl
{"ts": "2026-11-19T00:37:07.712+00:00", "request_id": "92cf28fb", "route": "/ask", "status": 200, "query": "90s track jacket in size M", "outcome": "fit_card", "item": "90s Track Jacket — Navy/White Stripe ($45.0, poshmark)", "error": null, "duration_ms": 9752, "waited_ms": 0, "model_calls": 2, "tokens_in": 730, "tokens_out": 182, "stages_ms": {"search_listings": 3849, "compare_price": 3902, "suggest_outfit": 1059, "create_fit_card": 941}}
{"ts": "2026-11-19T00:37:17.620+00:00", "request_id": "3930af13", "route": "/ask", "status": 200, "query": "silk slip dress in midi length under $40", "outcome": "fit_card", "item": "90s Silk Slip Dress — Floral, Midi Length ($30.0, depop)", "error": null, "duration_ms": 9559, "waited_ms": 0, "model_calls": 2, "tokens_in": 750, "tokens_out": 204, "stages_ms": {"search_listings": 3641, "compare_price": 3889, "suggest_outfit": 1188, "create_fit_card": 841}}
{"ts": "2026-11-19T00:37:27.335+00:00", "request_id": "b43d8366", "route": "/ask", "status": 200, "query": "platform sneakers size 8", "outcome": "fit_card", "item": "Platform Sneakers — White Chunky Sole ($48.0, poshmark)", "error": null, "duration_ms": 9072, "waited_ms": 0, "model_calls": 2, "tokens_in": 708, "tokens_out": 154, "stages_ms": {"search_listings": 3730, "compare_price": 3784, "suggest_outfit": 846, "create_fit_card": 712}}
{"ts": "2026-11-19T00:37:36.573+00:00", "request_id": "43023003", "route": "/ask", "status": 200, "query": "denim jacket under $50", "outcome": "fit_card", "item": "Denim Jacket — Light Wash, Cropped ($42.0, poshmark)", "error": null, "duration_ms": 9046, "waited_ms": 0, "model_calls": 2, "tokens_in": 708, "tokens_out": 172, "stages_ms": {"search_listings": 3584, "compare_price": 3603, "suggest_outfit": 925, "create_fit_card": 933}}
{"ts": "2026-11-19T00:37:45.787+00:00", "request_id": "7d0b5f6f", "route": "/ask", "status": 200, "query": "chunky knit cardigan", "outcome": "fit_card", "item": "Knit Cardigan — Chunky Brown ($35.0, depop)", "error": null, "duration_ms": 9440, "waited_ms": 0, "model_calls": 2, "tokens_in": 733, "tokens_out": 195, "stages_ms": {"search_listings": 3971, "compare_price": 3603, "suggest_outfit": 1081, "create_fit_card": 785}}
{"ts": "2026-11-19T00:37:55.395+00:00", "request_id": "554583ce", "route": "/ask", "status": 500, "query": "[1, 2]", "outcome": "crashed", "item": null, "error": "AttributeError: 'list' object has no attribute 'get'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T00:37:55.551+00:00", "request_id": "4a7bd452", "route": "/ask", "status": 500, "query": 42, "outcome": "crashed", "item": null, "error": "AttributeError: 'int' object has no attribute 'strip'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T00:37:55.739+00:00", "request_id": "b116d5a7", "route": "/ask", "status": 500, "query": "\"vintage tee\"", "outcome": "crashed", "item": null, "error": "AttributeError: 'str' object has no attribute 'get'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T00:37:55.897+00:00", "request_id": "babc3583", "route": "/ask", "status": 400, "query": "", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T00:37:56.052+00:00", "request_id": "4c315806", "route": "/ask", "status": 400, "query": "not json", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T00:37:56.206+00:00", "request_id": "bea74bf1", "route": "/ask", "status": 200, "query": "designer ballgown size XXS under $5", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'designer ballgown' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, nothing is listed under $5 (the cheapest listing is $12), and no listing comes in size XXS.", "duration_ms": 7239, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 7158}}
{"ts": "2026-11-19T00:38:03.446+00:00", "request_id": "8b771a91", "route": "/ask", "status": 200, "query": "wetsuit size XXS", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'wetsuit' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, no listing comes in size XXS.", "duration_ms": 7912, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 7910}}
```

## Trial 3

| Part | Request | Status | Client ms | X-Request-Id |
|---|---|---|---|---|
| c1 | `{"query": "90s track jacket in size M"}` | 200 | 9112 | 39947acb |
| c1 | `{"query": "silk slip dress in midi length under $40"}` | 200 | 9507 | 6e99785a |
| c1 | `{"query": "platform sneakers size 8"}` | 200 | 8970 | 24f76cfd |
| c1 | `{"query": "denim jacket under $50"}` | 200 | 9208 | 86f5ae30 |
| c1 | `{"query": "chunky knit cardigan"}` | 200 | 8851 | 8608942d |
| c2 | `[1, 2]` | 500 | 141 | None |
| c2 | `{"query": 42}` | 500 | 143 | None |
| c2 | `"vintage tee"` | 500 | 146 | None |
| c2 | `{"query": ""}` | 400 | 155 | 645aeb3a |
| c2 | `not json` | 400 | 136 | 6f895c17 |
| c3 | `{"query": "designer ballgown size XXS under $5"}` | 200 | 7843 | 9c1be737 |
| c3 | `{"query": "wetsuit size XXS"}` | 200 | 15538 | 9a9c7601 |

Log records after the mark:

```jsonl
{"ts": "2026-11-19T00:39:12.200+00:00", "request_id": "39947acb", "route": "/ask", "status": 200, "query": "90s track jacket in size M", "outcome": "fit_card", "item": "90s Track Jacket — Navy/White Stripe ($45.0, poshmark)", "error": null, "duration_ms": 8972, "waited_ms": 0, "model_calls": 2, "tokens_in": 721, "tokens_out": 162, "stages_ms": {"search_listings": 3656, "compare_price": 3703, "suggest_outfit": 936, "create_fit_card": 676}}
{"ts": "2026-11-19T00:39:21.328+00:00", "request_id": "6e99785a", "route": "/ask", "status": 200, "query": "silk slip dress in midi length under $40", "outcome": "fit_card", "item": "90s Silk Slip Dress — Floral, Midi Length ($30.0, depop)", "error": null, "duration_ms": 9374, "waited_ms": 0, "model_calls": 2, "tokens_in": 749, "tokens_out": 206, "stages_ms": {"search_listings": 4027, "compare_price": 3704, "suggest_outfit": 1022, "create_fit_card": 620}}
{"ts": "2026-11-19T00:39:30.864+00:00", "request_id": "24f76cfd", "route": "/ask", "status": 200, "query": "platform sneakers size 8", "outcome": "fit_card", "item": "Platform Sneakers — White Chunky Sole ($48.0, poshmark)", "error": null, "duration_ms": 8828, "waited_ms": 0, "model_calls": 2, "tokens_in": 709, "tokens_out": 149, "stages_ms": {"search_listings": 3491, "compare_price": 3795, "suggest_outfit": 828, "create_fit_card": 713}}
{"ts": "2026-11-19T00:39:39.862+00:00", "request_id": "86f5ae30", "route": "/ask", "status": 200, "query": "denim jacket under $50", "outcome": "fit_card", "item": "Denim Jacket — Light Wash, Cropped ($42.0, poshmark)", "error": null, "duration_ms": 9064, "waited_ms": 0, "model_calls": 2, "tokens_in": 710, "tokens_out": 167, "stages_ms": {"search_listings": 3692, "compare_price": 4097, "suggest_outfit": 605, "create_fit_card": 670}}
{"ts": "2026-11-19T00:39:49.086+00:00", "request_id": "8608942d", "route": "/ask", "status": 200, "query": "chunky knit cardigan", "outcome": "fit_card", "item": "Knit Cardigan — Chunky Brown ($35.0, depop)", "error": null, "duration_ms": 8712, "waited_ms": 0, "model_calls": 2, "tokens_in": 745, "tokens_out": 209, "stages_ms": {"search_listings": 3471, "compare_price": 3595, "suggest_outfit": 878, "create_fit_card": 767}}
{"ts": "2026-11-19T00:39:57.968+00:00", "request_id": "3231ba60", "route": "/ask", "status": 500, "query": "[1, 2]", "outcome": "crashed", "item": null, "error": "AttributeError: 'list' object has no attribute 'get'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T00:39:58.129+00:00", "request_id": "d4ffa0db", "route": "/ask", "status": 500, "query": 42, "outcome": "crashed", "item": null, "error": "AttributeError: 'int' object has no attribute 'strip'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T00:39:58.294+00:00", "request_id": "1beba22b", "route": "/ask", "status": 500, "query": "\"vintage tee\"", "outcome": "crashed", "item": null, "error": "AttributeError: 'str' object has no attribute 'get'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T00:39:58.581+00:00", "request_id": "645aeb3a", "route": "/ask", "status": 400, "query": "", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T00:39:58.790+00:00", "request_id": "6f895c17", "route": "/ask", "status": 400, "query": "not json", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T00:39:58.955+00:00", "request_id": "9c1be737", "route": "/ask", "status": 200, "query": "designer ballgown size XXS under $5", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'designer ballgown' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, nothing is listed under $5 (the cheapest listing is $12), and no listing comes in size XXS.", "duration_ms": 7691, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 7608}}
{"ts": "2026-11-19T00:40:06.646+00:00", "request_id": "9a9c7601", "route": "/ask", "status": 200, "query": "wetsuit size XXS", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'wetsuit' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, no listing comes in size XXS.", "duration_ms": 7699, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 7613}}
```
