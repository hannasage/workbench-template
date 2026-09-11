# log.md

Append only. One line per operation, newest at the bottom. Never edit a past
line. A mistake earns a new line that corrects it.

Format:

```
YYYY-MM-DD · ingest · raw/sources/<file> · created N, updated N
YYYY-MM-DD · query · <the question, short> · answered from N pages
YYYY-MM-DD · lint · <what failed> · <what was fixed>
YYYY-MM-DD · verify · <what was tested> · <what was corrected or moved>
YYYY-MM-DD · open-items · <file>#<id> · opened | closed by work: <what> | closed by the owner: <what>
```

A line starting `note ·` records something that happened to the wiki but was
not one of the five operations: a domain created, a claim dropped on purpose,
a schema change.

---

