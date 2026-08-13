# Archived for deletion

PRDs whose every decision now lives in the design docs. They are staged here so the deletion
is a deliberate, reviewable act rather than something an agent does mid-run.

**Nothing reads these.** They are not a source of truth, they are not maintained, and they are
not consulted when a question comes up — the design docs are. A PRD lands here only once a
`forge-harvest-planner` run reports it fully harvested, meaning every design doc it owed has
taken its content.

This folder deliberately sits **outside** the manifest's `prds` path, so no agent globbing that
directory can pick these up.

The intended lifetime is short. A staging folder that never empties becomes the second source
of truth this whole migration existed to remove — so delete from here, don't let it accumulate.
`git rm` is enough; git keeps the history, and `git log --diff-filter=D` finds anything again.

Replacements are generated fresh from the design docs when a feature is about to be built, and
only when that feature earns a PRD at all. Most will not.
