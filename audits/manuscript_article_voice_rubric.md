# Manuscript Article Voice Rubric

Use this rubric for an LLM-backed audit of whether each latest `manuscript.md`
reads like a standalone human-facing article rather than a reply to gatekeepers.
This is a judgment rubric, not a deterministic phrase scan. Short protocol
statements can be acceptable when they serve reproducibility, but the manuscript
must not depend on the reader knowing the review history.

## Inputs To Read

- the latest `manuscript.md` and `manuscript.pdf`;
- `revision_response.md`, `revision_plan.md`, issue ledger, and verification
  matrix for context only;
- `results.json`, figures, tables, and `display_item_explanations.md`;
- the run-level `manuscript_quality_contract.md` and article-type contract;
- referee reviews and integrity reports that requested manuscript changes.

## Judgment Questions

1. Does the manuscript read as a final article from title through references, or
   does it read like a changelog, rebuttal letter, audit memo, or response to
   reviewer questions?
2. Are review-process facts kept in `revision_response.md`, issue ledgers, and
   verification matrices rather than used as manuscript evidence?
3. When a revision added analysis, sensitivity checks, limitations, or
   clarification, did the manuscript integrate those changes as Methods, Results,
   Discussion, Limitations, or Data/Code Availability prose?
4. Can a reader understand the study without knowing which issue, Referee,
   Integrity Checker, or Editor request caused a change?
5. Does the Protocol Compliance section, if present, stay brief and article-style,
   avoiding a procedural inventory that overwhelms the scientific article?
6. Are limitations and reproducibility statements written as article claims rather
   than as direct answers to gatekeeper concerns?
7. Does the integrated `article/article.pdf`, when present, preserve the same
   article voice?

## Required Output

```json
{
  "judgment_type": "manuscript_article_voice",
  "status": "pass | revise | reject | cannot_judge",
  "article_voice_summary": "<one paragraph>",
  "process_prose_problems": [
    {
      "path": "<manuscript path>",
      "section": "<section or approximate location>",
      "problem": "<why this reads like review/process prose>",
      "rewrite_direction": "<how to convert it into article prose>"
    }
  ],
  "acceptable_protocol_statements": [],
  "required_revision_response_locations": [],
  "recommended_next_state": "accept_possible | revise_manuscript | require_editor_review | reject",
  "confidence": 0.0,
  "evidence_paths": []
}
```

## Decision Guidance

- `pass`: the manuscript is understandable as a standalone article, with any
  protocol statement brief and article-style.
- `revise`: the science may be adequate, but manuscript prose still answers the
  review process or narrates revision mechanics.
- `reject`: the manuscript is mostly a response memo, audit trail, or generated
  package summary rather than an article.
- `cannot_judge`: required manuscript or revision-context artifacts are missing.
