# Jordan source audit — 2026-08-09

## Outcome

The Jordan pilot now has three strict source adapters, an immutable capture path and one exact official PDF capture. It does **not** yet have publishable verified observations. The real Q1 2026 unemployment parser passed, but its output remains quarantined because reuse permission is unresolved and the independent review is unsigned. Software and capture provenance are anchored to commit `29e916ca3350ba748f30022e0353f35de210121b`.

## Exact capture completed

| Field | Recorded value |
| --- | --- |
| Artifact | Jordan DoS Q1 2026 unemployment PDF |
| Pages | 10 |
| Bytes | 1,651,606 |
| SHA-256 | `b3627bd4d5e5dbfc55f289a645dbc0f2ed8924b15bab027dd4b1f4d51c633f96` |
| Publisher release time | `2026-06-17T12:08:09+03:00` |
| Capture time | `2026-08-09T16:29:19.277475+00:00` |
| Parser result | 16.1%, `ALL_RESIDENTS`, `2026-Q1` |
| Status | Quarantined |
| Provenance commit | `29e916ca3350ba748f30022e0353f35de210121b` |

The PDF's page 2 chart was visually inspected after Poppler rendering. It contains 51 sex-by-quarter cells for Q1 2022 through Q1 2026. Those cells were transcribed as a retrospective snapshot with the **2026-06-17 vintage**; they are not mislabeled as contemporaneous historical vintages. The transcription is retained in the rights-pending private audit workspace and is not distributed in the public repository.

The publisher's [terms page](https://dosweb.dos.gov.jo/terms-conditions/) states that website information is subject to copyright unless noted otherwise. No redistribution grant was found. Original PDF bytes are therefore withheld from the public bundle while the hash, source link, byte length and provenance receipt remain public.

## Official-source findings

| Family | Official evidence | Finding | Machine status |
| --- | --- | --- | --- |
| Macro/monetary database | [CBJ Statistical Database](https://www.cbj.gov.jo/En/Pages/Statistical_Database) | Covers monetary/banking, public finance, balance of payments, trade, GDP, prices, production and market indicators | Source discovered; general database adapter pending |
| Policy rate | [CBJ monetary-policy interest-rate history](https://www.cbj.gov.jo/en/pages/climateinstruments) | Dated policy-instrument histories are published; decisions also appear as separate releases | Strict key-rate decision parser implemented |
| Q1 2026 unemployment | [Jordan DoS press release](https://dosweb.dos.gov.jo/databank/News/Unemployment/2026/unemp_Q1_2026_en.pdf) | Total resident unemployment was reported as 16.1%; Jordanian sex-specific rates are different concepts | Strict total-population parser implemented |
| CPI | [Jordan DoS CPI archive](https://dosweb.dos.gov.jo/category/news/cpi/) | Monthly year-on-year and cumulative rates can coexist in the same release | Strict monthly year-on-year parser implemented |
| Release history | [Jordan DoS unemployment archive](https://dosweb.dos.gov.jo/category/news/unemployment-rate/) | Page timestamps provide evidence of publication timing, but not a contractual calendar | Observed calendar recorded; exact time required per capture |

## Definition break found

The public releases use several unemployment populations: all residents, Jordanians, Jordanian males and Jordanian females. A series called only `unemployment.total` is not safe. The alpha therefore uses:

- `labor.unemployment.total_population` with entity `ALL_RESIDENTS`;
- `labor.unemployment.jordanian_population` for Jordanian-only totals when separately onboarded;
- future sex-specific series with explicit population and sex dimensions.

The parser requires the phrase “total population” or “entire population” near the value and reference quarter. If that evidence is absent or conflicting, ingestion fails.

## CPI ambiguity found

Jordan DoS releases can report monthly year-on-year inflation, month-on-month inflation and a cumulative year-to-date rate in the same document. The CPI adapter only accepts the rate explicitly tied to “compared to the same month” and maps it to `prices.cpi.headline_yoy`. Other measures require separate series and parsers.

## Remaining blockers

1. Have a reviewer other than the adapter/transcription author complete the frozen 20-cell packet.
2. Score the returned packet with 100% value and scope agreement or resolve every mismatch publicly.
3. Obtain permission or a legal determination for redistribution; until then keep raw bytes withheld.
4. Capture and audit the CPI and CBJ policy-rate sources.
5. Attach the provenance commit to any rows restored after permission, rerun the release verifier and publish checksums.

Until these gates pass, the discovery ledger is research planning evidence—not a dataset release.
