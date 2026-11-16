# Father Health Center

[![HTML Guardian](https://github.com/74127418528426leo-del/Father-Health-Center/actions/workflows/html-guardian.yml/badge.svg)](https://github.com/74127418528426leo-del/Father-Health-Center/actions/workflows/html-guardian.yml)

**Live app:** https://74127418528426leo-del.github.io/Father-Health-Center/

## Continuous checks

The **HTML Guardian** workflow runs on every push, on pull requests targeting `main`, every 15 minutes, and on demand.

It:

- validates every HTML file in the repository with a pinned HTML validator;
- checks the syntax of every inline JavaScript block without executing it;
- checks that the published GitHub Pages app returns HTTP 200 and the expected title on scheduled and manual runs;
- writes a readable run summary and detailed logs in the [Actions tab](https://github.com/74127418528426leo-del/Father-Health-Center/actions/workflows/html-guardian.yml).

Existing single-file style and accessibility findings are visible as warnings; structural errors that cannot be safely auto-fixed fail the check and remain visible in the run log.

## Open the live status

Go to [HTML Guardian runs](https://github.com/74127418528426leo-del/Father-Health-Center/actions/workflows/html-guardian.yml), open the newest run, then select **Summary** for the result or a job for detailed logs.

GitHub scheduled runs can be delayed during high load. Push and pull-request checks run when those events arrive.
