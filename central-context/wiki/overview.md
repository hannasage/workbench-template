---
type: overview
status: draft
created: 2026-09-11
updated: 2026-09-12
sources: []
---
# overview

The map of active domains. Every domain gets one row, and the row says what
the domain covers, not what is in it.

No domains yet. A domain is created when a third source lands on the same
subject, and `wiki-ingest` writes the row when it creates one.

## Key points

- Nothing is ingested. `raw/sources/` is empty.

## Domains

| Domain | Covers | Pages |
|---|---|---|

## Links

- [[index]], the catalog, at the root of the knowledge base.
- The page schema is `central-context/AGENTS.md`, at that same root. It stays a
  path, because the clone root ships a second file of that name.
- No second page exists under `wiki/` yet. The first ingest writes one.

## Open questions

- Which domains this workbench will actually need. That is answered by
  ingesting sources, not by deciding up front.
