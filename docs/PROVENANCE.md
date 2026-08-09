# Provenance and correction protocol

## Capture record

Each retrieval records source ID, requested URL, response time, HTTP metadata when available, byte length, content type, SHA-256, retrieval agent version and storage key. If redistribution is prohibited, the system retains the permitted metadata and canonical source reference while access to source bytes remains restricted.

## Transformation record

A canonical observation is reproducible from:

1. source hash;
2. adapter name and version;
3. transformation parameters;
4. parent observation IDs for derived series;
5. environment lockfile;
6. Git commit.

## Corrections

- Source revision: append a row with the publisher's new release time and revision sequence.
- Lab parsing error: quarantine affected rows, publish an incident note, regenerate corrected rows and retain the invalid artifact in the audit log.
- Rights issue: remove restricted bytes from public distribution while retaining a tombstone and non-restricted provenance metadata.
- Entity-resolution error: version the relationship edge; never rewrite historical ownership silently.

## Hash boundary

`source_hash` hashes the retrieved source bytes before normalization. Export files have their own release checksum manifest. These are different objects and must never share a field.
