---
description: Create or update the feature specification from a natural language feature description.
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

The text the user typed after `/specify` in the triggering message **is** the feature description. Assume you always have it available in this conversation even if `$ARGUMENTS` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

Given that feature description, do this:

1. Run the script `.specify/scripts/bash/create-new-feature.sh --json "$ARGUMENTS"` from repo root and parse its JSON output for `BRANCH_NAME`, `FEATURE_NUM`, `SPEC_FILE`, and `REQUIREMENTS`.
  - **IMPORTANT** You must only ever run this script once. The JSON is provided in the terminal as output - always refer to it to get the actual content you're looking for.
  - `REQUIREMENTS` is a list of guides with pre-extracted requirement text. Preserve the order delivered by the script.
2. Load `.specify/templates/spec-template.md` to understand required sections.
3. Populate the `## Guide Requirements` section of the spec using the JSON data:
  - Group requirements by guide, numbering each requirement.
  - Include the guide title and relative path so the user can trace it back to the source guide.
  - If a requirement is intentionally deferred, annotate it with `[NEEDS WAIVER]` to signal `/waive-requirement` follow-up work.
  - If `REQUIREMENTS` is empty, remove the section or explicitly state that no guide requirements were discovered.
4. Complete the remaining sections of the template, replacing placeholders with concrete details derived from the feature description (arguments) while preserving section order and headings.
5. Report completion with branch name, spec file path, and readiness for the next phase.

Note: The script creates and checks out the new branch and initializes the spec file before writing.
