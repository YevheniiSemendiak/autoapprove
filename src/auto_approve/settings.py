import os
from dataclasses import dataclass, field

from .checks import parse_list


@dataclass(frozen=True)
class Settings:
    token: str = field(repr=False)
    owners: list[str]
    allowed_authors: list[str]
    required_label: str | None
    dry_run: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            token=os.environ["GH_TOKEN"],
            owners=parse_list(os.environ["LIST_OF_OWNERS"]),
            allowed_authors=parse_list(os.environ["ALLOWED_AUTHORS"]),
            required_label=os.environ.get("REQUIRED_LABEL"),
            dry_run=os.environ.get("DRY_RUN", "false").lower() in ("1", "true", "yes"),
        )
