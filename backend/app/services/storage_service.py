from pathlib import Path

import structlog

from app.config import settings

logger = structlog.get_logger(__name__)


class StorageError(Exception):
    """Raised when a storage operation fails."""


class StorageService:
    def __init__(self, base_path: str | None = None) -> None:
        self._base = Path(base_path or settings.storage_path).resolve()

    def save_pdf(self, user_id: str, analysis_id: str, file_bytes: bytes) -> str:
        """
        Persist a PDF to local filesystem.

        Returns the relative storage path (relative to base_path).
        Structure: {user_id}/{analysis_id}/copia_literal.pdf
        """
        dest_dir = self._base / user_id / analysis_id
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_file = dest_dir / "copia_literal.pdf"
            dest_file.write_bytes(file_bytes)
            relative_path = str(Path(user_id) / analysis_id / "copia_literal.pdf")
            logger.info(
                "pdf_saved",
                user_id=user_id,
                analysis_id=analysis_id,
                path=relative_path,
            )
            return relative_path
        except OSError as exc:
            logger.error("pdf_save_error", error=str(exc))
            raise StorageError(f"Failed to save PDF: {exc}") from exc

    def get_pdf_path(self, storage_path: str) -> Path:
        """
        Resolve a relative storage path to an absolute filesystem path.

        Raises StorageError if the file does not exist.
        """
        full_path = self._base / storage_path
        if not full_path.exists():
            raise StorageError(f"PDF not found at path: {storage_path}")
        return full_path

    def ensure_storage_dir(self) -> None:
        """Create the base storage directory if it does not exist."""
        try:
            self._base.mkdir(parents=True, exist_ok=True)
            logger.info("storage_dir_ready", path=str(self._base))
        except OSError as exc:
            logger.error("storage_dir_error", error=str(exc))
            raise StorageError(f"Failed to create storage directory: {exc}") from exc


_storage_service: StorageService | None = None


def get_storage_service_singleton() -> StorageService:
    """Return the singleton StorageService instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
        _storage_service.ensure_storage_dir()
    return _storage_service
