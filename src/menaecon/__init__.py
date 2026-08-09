"""Public interface for menaecon."""

from .client import MenaClient, QueryResult

__all__ = ["MenaClient", "QueryResult", "mena"]
__version__ = "0.2.0a1"

class _LazyClient:
    """Create the default local warehouse only when the client is actually used."""

    _client: MenaClient | None = None

    def _get_client(self) -> MenaClient:
        if self._client is None:
            self._client = MenaClient()
        return self._client

    def __getattr__(self, name: str):
        return getattr(self._get_client(), name)


# Importing menaecon is side-effect free; `mena.get(...)` initializes on first use.
mena = _LazyClient()
