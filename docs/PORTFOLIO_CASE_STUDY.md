# Portfolio case study — MENA Economic Terminal

> Economic data infrastructure designed to answer: what could a researcher have known on a particular date?

[Portfolio](https://layan-research-portfolio.r8ms5bfzb6.chatgpt.site) · [Repository overview](../README.md)

## The infrastructure problem

Most economic databases expose the latest revised value. That is insufficient for real-time forecasting, policy event studies and communication-shock research, where the relevant information set is what had actually been released by the event date.

The Terminal stores release time, vintage, revision, source artifact, retrieval time, transformation, license status, source hash and Git provenance as part of the observation contract.

## Current executable alpha

**v0.2.0a1** includes:

- vintage-safe queries and revision-aware selection;
- immutable content-addressed capture with SHA-256 manifests;
- strict Jordan unemployment, CPI and policy-rate adapters;
- row-level quality status and quarantine;
- CLI and optional API surfaces;
- synthetic fixtures and **31 passing tests** at the alpha release;
- an exact Q1 2026 Jordan unemployment source capture and successful real-parser result.

## The integrity decision

The rights-pending 51-cell Jordan transcription is not distributed in the public tree. Parsing does not make a row verified: reuse rights, release-time evidence, independent source comparison and row-level Git provenance are separate gates.

This is a feature of the research design, not missing fine print.

## Proof maturity

| Layer | Current state |
| --- | --- |
| Software architecture | Public and executable |
| Tests | Passing at alpha release |
| Exact source capture | Completed for first Jordan source |
| Official-data distribution | Quarantined pending rights review |
| Independent source audit | Not yet signed |
| Regional coverage | Roadmap, not a completed database claim |

## Next validation gate

Rights clarification, a signed external source-document audit and promotion of the first official observations through the public release verifier.
