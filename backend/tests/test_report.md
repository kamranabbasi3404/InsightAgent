# InsightAgent Automated Test Report
**Date:** 2026-07-16 20:29:23

## Summary Metrics
- **Total Queries Executed:** 20
- **Routing Accuracy:** 90.0% (18/20)
- **System Verification Pass Rate:** 90.0% (18/20)
- **Average Response Time:** 44.38 seconds
- **Routing Success Criteria (>=90%):** ✅ PASSED

## Routing Performance by Category
| Route Category | Queries | Route Matches | Accuracy | Checks Passed | Pass Rate |
|---|---|---|---|---|---|
| no_retrieval | 5 | 5 | 100.0% | 5 | 100.0% |
| local_only | 5 | 4 | 80.0% | 4 | 80.0% |
| web_only | 5 | 4 | 80.0% | 4 | 80.0% |
| hybrid | 5 | 5 | 100.0% | 5 | 100.0% |

## Detailed Query Run Log
| ID | Query | Expected Route | Actual Route | Citations | Trace Steps | Time | Verification |
|---|---|---|---|---|---|---|---|
| 1 | Hello there, how's it going? | no_retrieval | no_retrieval | 0 | 2 | 4.16s | ✅ PASS |
| 2 | What are your core capabilities as an assistant? | no_retrieval | no_retrieval | 0 | 2 | 4.74s | ✅ PASS |
| 3 | Can you write a python script to reverse a string? | no_retrieval | no_retrieval | 0 | 2 | 4.09s | ✅ PASS |
| 4 | What is 25 * 40? | no_retrieval | no_retrieval | 0 | 2 | 4.56s | ✅ PASS |
| 5 | Tell me a joke about computers. | no_retrieval | no_retrieval | 0 | 2 | 3.91s | ✅ PASS |
| 6 | What was the total value of Pakistan's IT exports in fiscal year 2023-2024 according to the report? | local_only | local_only | 4 | 6 | 12.93s | ✅ PASS |
| 7 | What are the government tax rate and foreign currency rules for IT exporters according to the 2024 report? | local_only | local_only | 4 | 6 | 24.50s | ✅ PASS |
| 8 | According to local reports, what is the Special Technology Zones Authority (STZA) tax exemption duration? | local_only | local_only | 4 | 6 | 24.09s | ✅ PASS |
| 9 | What are the key infrastructure challenges faced by Pakistan's IT sector mentioned in the report? | local_only | local_only | 4 | 6 | 23.59s | ✅ PASS |
| 10 | What does the 2024 report project for Pakistan's IT exports in 2026 under a stable tax policy? | local_only | hybrid | 9 | 15 | 95.66s | ❌ FAIL<br><small>Route mismatch: expected 'local_only', got 'hybrid'</small> |
| 11 | Who is the current Prime Minister of Pakistan in 2026? | web_only | web_only | 5 | 6 | 33.60s | ✅ PASS |
| 12 | What was Pakistan's annual inflation rate in 2025? | web_only | hybrid | 9 | 15 | 108.06s | ❌ FAIL<br><small>Route mismatch: expected 'web_only', got 'hybrid'</small> |
| 13 | Who won the ICC Men's T20 World Cup in 2026? | web_only | web_only | 5 | 9 | 47.39s | ✅ PASS |
| 14 | What is the current stock price of Google (Alphabet Inc.) today? | web_only | web_only | 5 | 9 | 50.44s | ✅ PASS |
| 15 | What is the latest weather forecast for Karachi right now? | web_only | web_only | 5 | 9 | 46.52s | ✅ PASS |
| 16 | How do Pakistan's IT exports in 2023-2024 compare with the latest figures for 2025 or 2026? | hybrid | hybrid | 9 | 15 | 97.41s | ✅ PASS |
| 17 | Are the current IT export tax rates in Pakistan different from the 0.25% policy outlined in the 2024 report? | hybrid | hybrid | 9 | 7 | 67.40s | ✅ PASS |
| 18 | Has the Special Technology Zones Authority (STZA) introduced any new incentives in 2025/2026 beyond the 10-year tax exemptions listed in the 2024 report? | hybrid | hybrid | 9 | 11 | 66.90s | ✅ PASS |
| 19 | Compare the projections of Pakistan's IT exports reaching $3.5 billion by 2026 from the report with actual 2025/2026 export data. | hybrid | hybrid | 9 | 15 | 106.32s | ✅ PASS |
| 20 | Is PayPal now available in Pakistan in 2026, or is it still a challenge as reported in 2024? | hybrid | hybrid | 9 | 7 | 61.36s | ✅ PASS |