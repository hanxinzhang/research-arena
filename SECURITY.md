# Security And Safety Notes

Research Arena is an experimental LLM-native research workflow protocol. Treat all
agent-generated outputs and generated code as untrusted until reviewed.

## Current Safety Boundaries

- The repository should not contain credentials, API keys, private paths, or personal
  secrets.
- The project does not require an in-repo API key, service token, `.env` file, or
  project-specific LLM server.
- Your chosen LLM agent may use repository files and user-provided prompts as model
  context. Do not place private data or secrets in the repo unless you intend that
  LLM agent to see them.
- Agents may browse for literature when internet access is available, but should not
  paste private/local data into search engines, external websites, or third-party
  literature tools.
- Do not commit private prompts, private datasets, generated run folders, or
  sensitive artifacts.
- The included OASIS CSV is the intended public/demo quickstart dataset.
- Generated analysis scripts should be inspected before execution.
- Generated analysis scripts should avoid network calls, shell calls, private paths,
  credentials, hidden external files, and destructive file operations.
- Toolchain, manuscript-render, article-build, and final-output reports should
  sanitize repository, home-directory, staged-tool, and temporary paths before they
  are copied into shareable outputs.

## Before Uploading To GitHub

Before publishing or re-uploading the repository:

1. Upload the framework folder, not local test-run folders, unless the test run has
   been intentionally cleaned and reviewed.
2. Keep local datasets, generated `runs/`, `submissions/`, `work_packets/`,
   `human_readable_outputs/`, `outputs/`, and agent workspaces out of the public
   repository unless redistribution is explicitly allowed.
3. Run a final local scan for credentials and private paths:

   ```bash
   rg -n "(api[_-]?key|secret|password|bearer|authorization|credential|private[_-]?key|ghp_|sk-)" .
   rg -n "(/Users/|/private/var/folders|/private/tmp|/tmp/)" .
   find . -name ".DS_Store" -o -path "*/__pycache__/*" -o -name "*.pyc"
   ```

4. Treat any generated analysis code as untrusted until it has been inspected for
   network calls, shell calls, private paths, hidden dependencies, and destructive
   operations.
5. Confirm the source dataset license, citation terms, consent terms, and
   redistribution rules before publishing any data-derived artifact.

## Generated Code Risk

LLM agents can write useful analysis code, but generated code is still code. For real
or sensitive data, use an isolated workspace with:

- no ambient credentials;
- explicit dataset copies;
- restricted outbound network access when running generated scripts;
- human inspection before execution;
- artifact review before sharing.

## Data Safety

The included OASIS table is a small public/demo dataset with study-style identifiers
and clinical/cognitive variables. It does not include names, emails, phone numbers,
addresses, SSNs, or dates of birth based on the local scan, but it is still
human-participant-derived data. Check the source dataset's license, citation terms,
consent terms, and redistribution rules before public release or reuse.

## Scientific Safety

Research Arena outputs are exploratory. They are not medical advice, diagnostic
evidence, causal discovery, or validated science. Human review is required before
using any output for scientific, clinical, policy, or operational decisions.

## Reporting Issues

If this repository is published on GitHub, report security or privacy concerns through
GitHub issues only if they do not expose sensitive material. For sensitive disclosures,
use a private contact channel maintained by the repository owner.
