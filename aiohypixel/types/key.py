from dataclasses import dataclass


@dataclass
class Key:
    """Object representing a Hypixel API key."""

    key: str
    owner: str
    limit: int
    queries_in_past_minute: int
    total_queries: int
