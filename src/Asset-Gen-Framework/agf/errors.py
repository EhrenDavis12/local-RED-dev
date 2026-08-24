"""
The CLI's own error vocabulary — cli-v1 R5, R28.

Every command failure the CLI reports on its own (as opposed to an exception
escaping from somewhere unanticipated, which R4/R28 catch generically as exit
11) is one of these. Each carries the exit code R28 assigns it, a non-empty
`message` stating what failed, and a non-empty `remedy` stating what to
change (R5).
"""
from __future__ import annotations


class AgfError(Exception):
    """Base class for every error the CLI raises deliberately."""

    def __init__(self, code: int, message: str, remedy: str, checks=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.remedy = remedy
        self.checks = checks


class UsageError(AgfError):
    """R28 code 1 — unknown command, wrong argument count, unknown option."""

    def __init__(self, message: str, remedy: str = "correct the command line and try again"):
        super().__init__(1, message, remedy)


class ConfigError(AgfError):
    """R28 code 2 — config missing, unparseable, or a declared path is wrong."""

    def __init__(self, message: str, remedy: str = "fix assetgen.yaml and try again"):
        super().__init__(2, message, remedy)


class ManifestError(AgfError):
    """R28 code 3 — manifest missing, unparseable, or an entry is invalid."""

    def __init__(self, message: str, remedy: str = "fix the manifest and try again"):
        super().__init__(3, message, remedy)


class NotFoundError(AgfError):
    """R28 code 4 — no entry by that name."""

    def __init__(self, message: str, remedy: str = "check the entry name against the manifest"):
        super().__init__(4, message, remedy)


class CredentialError(AgfError):
    """R28 code 5 — credential absent from the environment."""

    def __init__(
        self,
        message: str,
        remedy: str = "set REPLICATE_API_TOKEN in the environment and try again",
    ):
        super().__init__(5, message, remedy)


class ProviderCallError(AgfError):
    """R28 code 6 — the provider rejected, failed or could not be reached."""

    def __init__(
        self,
        message: str,
        remedy: str = "check the provider's response and retry, or fix the entry's inputs",
    ):
        super().__init__(6, message, remedy)


class ChecksFailedError(AgfError):
    """R28 code 7 — a check in R71's list failed; nothing was committed."""

    def __init__(self, message: str, remedy: str, checks):
        super().__init__(7, message, remedy, checks=checks)


class RefusedError(AgfError):
    """R28 code 8 — R18: the entry's output already exists."""

    def __init__(self, message: str, remedy: str = "run 'agf regenerate <name>' to replace it"):
        super().__init__(8, message, remedy)


class BusyError(AgfError):
    """R28 code 9 — another run holds the run lock."""

    def __init__(
        self, message: str, remedy: str = "wait for the other run to finish and try again"
    ):
        super().__init__(9, message, remedy)


class DestinationError(AgfError):
    """R28 code 10, "Destination" — the output could not be placed where the
    entry declared it, by either route: the result passed its checks and
    the commit rename failed (R67), or a directory on the way to it could
    not be created because a file occupies that path (R12)."""

    def __init__(self, message: str, remedy: str):
        super().__init__(10, message, remedy)


class RecordCorruptError(AgfError):
    """R28 code 13 — R76: the record file exists and cannot be read as a
    valid record. The framework never repairs or overwrites it; deleting it
    is the stated remedy."""

    def __init__(self, message: str, remedy: str):
        super().__init__(13, message, remedy)


class InternalError(AgfError):
    """R28 code 11 — an unexpected failure. The traceback goes to stderr."""

    def __init__(self, message: str, remedy: str = "see the stderr traceback for details"):
        super().__init__(11, message, remedy)


class ExtractionFailedError(AgfError):
    """R28 code 12 — the source video could not be read or decoded (R74)."""

    def __init__(self, message: str, remedy: str):
        super().__init__(12, message, remedy)
