# measure.py — hosted

- Server: https://fitfindr-am5n.onrender.com
- When: 2026-11-18 18:26
- GET /health first: 200 in 314 ms
- Produced by: `measure.py::main`; the records come from `serve.py::ask`, via GET /log

| # | Request | Status | Client ms | Server duration_ms | Outcome | Model calls | Tokens in | Tokens out |
|---|---|---|---|---|---|---|---|---|
| 1 | `{"query": "vintage graphic tee under $30"}` | 200 | 25777 | 25623 | fit_card | 2 | 726 | 188 |
| 2 | `{"query": "90s track jacket in size M"}` | 200 | 12788 | 12404 | fit_card | 2 | 724 | 184 |
| 3 | `{"query": "silk slip dress in midi length under $40"}` | 200 | 10178 | 9835 | fit_card | 2 | 771 | 218 |
| 4 | `{"query": "platform sneakers size 8"}` | 200 | 10259 | 10126 | fit_card | 2 | 712 | 180 |
| 5 | `{"query": "denim jacket under $50"}` | 200 | 9737 | 9410 | fit_card | 2 | 726 | 180 |
| 6 | `{"query": "chunky knit cardigan"}` | 200 | 10168 | 10018 | fit_card | 2 | 748 | 199 |
| 7 | `{"query": "cargo pants under $30"}` | 200 | 9385 | 9229 | fit_card | 2 | 715 | 162 |
| 8 | `{"query": "y2k baby tee"}` | 200 | 10278 | 9899 | fit_card | 2 | 724 | 181 |
| 9 | `{"query": "corduroy pants"}` | 200 | 10464 | 10328 | fit_card | 2 | 708 | 160 |
| 10 | `{"query": "mini shoulder bag"}` | 200 | 10739 | 10596 | fit_card | 2 | 721 | 197 |
| 11 | `{"query": ""}` | 400 | 140 | 0 | rejected | 0 | 0 | 0 |
| 12 | `[1, 2]` | 500 | 132 | 0 | crashed | 0 | 0 | 0 |

**Averages over the 10 completed runs (outcome fit_card):** client 11977 ms · server 11747 ms · model calls 2 · tokens in 728 · tokens out 185

## The log records, as GET /log returned them

```jsonl
{"ts": "2026-11-18T23:24:14.292+00:00", "request_id": "ae98d068", "route": "/ask", "status": 200, "query": "vintage graphic tee under $30", "outcome": "fit_card", "item": "Vintage Band Tee — Faded Grey ($19.0, depop)", "error": null, "duration_ms": 25623, "waited_ms": 0, "model_calls": 2, "tokens_in": 726, "tokens_out": 188, "stages_ms": {"search_listings": 9110, "compare_price": 3907, "suggest_outfit": 8579, "create_fit_card": 4025}}
{"ts": "2026-11-18T23:24:40.042+00:00", "request_id": "b54c2876", "route": "/ask", "status": 200, "query": "90s track jacket in size M", "outcome": "fit_card", "item": "90s Track Jacket — Navy/White Stripe ($45.0, poshmark)", "error": null, "duration_ms": 12404, "waited_ms": 0, "model_calls": 2, "tokens_in": 724, "tokens_out": 184, "stages_ms": {"search_listings": 3961, "compare_price": 4211, "suggest_outfit": 3533, "create_fit_card": 699}}
{"ts": "2026-11-18T23:24:53.028+00:00", "request_id": "58d7503c", "route": "/ask", "status": 200, "query": "silk slip dress in midi length under $40", "outcome": "fit_card", "item": "90s Silk Slip Dress — Floral, Midi Length ($30.0, depop)", "error": null, "duration_ms": 9835, "waited_ms": 0, "model_calls": 2, "tokens_in": 771, "tokens_out": 218, "stages_ms": {"search_listings": 3883, "compare_price": 4098, "suggest_outfit": 950, "create_fit_card": 904}}
{"ts": "2026-11-18T23:25:03.019+00:00", "request_id": "dbd97c03", "route": "/ask", "status": 200, "query": "platform sneakers size 8", "outcome": "fit_card", "item": "Platform Sneakers — White Chunky Sole ($48.0, poshmark)", "error": null, "duration_ms": 10126, "waited_ms": 0, "model_calls": 2, "tokens_in": 712, "tokens_out": 180, "stages_ms": {"search_listings": 4080, "compare_price": 4206, "suggest_outfit": 995, "create_fit_card": 844}}
{"ts": "2026-11-18T23:25:13.266+00:00", "request_id": "2b53e9cf", "route": "/ask", "status": 200, "query": "denim jacket under $50", "outcome": "fit_card", "item": "Denim Jacket — Light Wash, Cropped ($42.0, poshmark)", "error": null, "duration_ms": 9410, "waited_ms": 0, "model_calls": 2, "tokens_in": 726, "tokens_out": 180, "stages_ms": {"search_listings": 3839, "compare_price": 3909, "suggest_outfit": 816, "create_fit_card": 845}}
{"ts": "2026-11-18T23:25:23.025+00:00", "request_id": "836562a2", "route": "/ask", "status": 200, "query": "chunky knit cardigan", "outcome": "fit_card", "item": "Knit Cardigan — Chunky Brown ($35.0, depop)", "error": null, "duration_ms": 10018, "waited_ms": 0, "model_calls": 2, "tokens_in": 748, "tokens_out": 199, "stages_ms": {"search_listings": 4069, "compare_price": 4106, "suggest_outfit": 1137, "create_fit_card": 705}}
{"ts": "2026-11-18T23:25:33.184+00:00", "request_id": "38e2d0f1", "route": "/ask", "status": 200, "query": "cargo pants under $30", "outcome": "fit_card", "item": "Low-Rise Cargo Pants — Khaki ($27.0, poshmark)", "error": null, "duration_ms": 9229, "waited_ms": 0, "model_calls": 2, "tokens_in": 715, "tokens_out": 162, "stages_ms": {"search_listings": 3810, "compare_price": 3906, "suggest_outfit": 962, "create_fit_card": 549}}
{"ts": "2026-11-18T23:25:42.562+00:00", "request_id": "02cc7241", "route": "/ask", "status": 200, "query": "y2k baby tee", "outcome": "fit_card", "item": "Y2K Baby Tee — Butterfly Print ($18.0, depop)", "error": null, "duration_ms": 9899, "waited_ms": 0, "model_calls": 2, "tokens_in": 724, "tokens_out": 181, "stages_ms": {"search_listings": 4246, "compare_price": 4001, "suggest_outfit": 943, "create_fit_card": 707}}
{"ts": "2026-11-18T23:25:52.853+00:00", "request_id": "ab283328", "route": "/ask", "status": 200, "query": "corduroy pants", "outcome": "fit_card", "item": "Corduroy Wide-Leg Pants — Rust ($32.0, depop)", "error": null, "duration_ms": 10328, "waited_ms": 0, "model_calls": 2, "tokens_in": 708, "tokens_out": 160, "stages_ms": {"search_listings": 4560, "compare_price": 3813, "suggest_outfit": 1173, "create_fit_card": 699}}
{"ts": "2026-11-18T23:26:03.324+00:00", "request_id": "39a04dfb", "route": "/ask", "status": 200, "query": "mini shoulder bag", "outcome": "fit_card", "item": "Mini Shoulder Bag — Tan Leather ($38.0, poshmark)", "error": null, "duration_ms": 10596, "waited_ms": 0, "model_calls": 2, "tokens_in": 721, "tokens_out": 197, "stages_ms": {"search_listings": 4071, "compare_price": 4407, "suggest_outfit": 921, "create_fit_card": 1196}}
{"ts": "2026-11-18T23:26:14.062+00:00", "request_id": "7c2534fd", "route": "/ask", "status": 400, "query": "", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-18T23:26:14.182+00:00", "request_id": "7f468d3b", "route": "/ask", "status": 500, "query": "[1, 2]", "outcome": "crashed", "item": null, "error": "AttributeError: 'list' object has no attribute 'get'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
```
