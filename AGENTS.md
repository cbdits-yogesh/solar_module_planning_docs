## Implementation Guidelines

- Reconcile the log (the progress) after each phase of documentation in docs/logs/LIFECYCLE_EXECUTION_LOG.md

## Implementation Plan

- Always create an implementation plan before proceeding
- User review it and might provide some feedback or comment, then he/she will ask to proceed (click Proceed button)

## File Modification & Review Synchronization Standards

### 1. File Delivery & Review Conflict Prevention
- **End-of-Task Delivery (Default):** Complete all code implementations, internal iterations, and test validations *before* presenting final changes to the user for acceptance. Avoid presenting intermediate file diffs that will immediately be re-edited.
- **Pause on Review (Interactive / Mid-Task Checkpoints):** If file changes are presented to the user for acceptance during a multi-step task, **pause and wait for user acceptance** before making any further edits or running tests that touch those same files. Never make subsequent edits to files pending user acceptance.

### 2. Atomic Writes & No Empty Placeholders
- Never create empty placeholder files (avoid `touch <file>` or 0-byte writes) prior to writing real content. Write the complete file atomically in a single operation.
- If an editor tab in VS Code was opened empty before write completion, close and reopen the tab or run `File: Revert File` to reload disk content. **Never press Ctrl+S on an empty tab**.

### 3. Post-Write Verification & No Premature Staging
- Immediately verify file integrity on disk (`ls -lh`, `wc -l`) after creating or editing files, and report file path, size, and line count in the final response.
- Do not run `git add` automatically unless explicitly instructed by the user, keeping changes in the working tree so VS Code's Source Control clearly displays unstaged modifications.

<!-- ## Planning / Spec-ing

Use Tracer bullets comes from the Pragmatic Programmer. When building systems, you want to write code that gets you feedback as quickly as possible. Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development.

-->
