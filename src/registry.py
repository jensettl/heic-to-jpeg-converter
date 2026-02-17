"""Conversion registry: defines valid routes and guards against invalid ones."""

from dataclasses import dataclass
from enum import Enum

from .converters.base import BaseConverter
from .converters.image import ImageConverter
from .converters.video import VideoConverter
from .converters.audio import AudioConverter
from .converters.document import DocumentConverter


class MediaType(Enum):
    """Broad media domains used to block cross-type conversions."""
    IMAGE    = "image"
    VIDEO    = "video"
    AUDIO    = "audio"
    DOCUMENT = "document"


# Maps every known extension to its media domain
EXTENSION_MEDIA_TYPE: dict[str, MediaType] = {
    # Images
    "heic": MediaType.IMAGE,
    "jpg":  MediaType.IMAGE,
    "jpeg": MediaType.IMAGE,
    "png":  MediaType.IMAGE,
    "webp": MediaType.IMAGE,
    "gif":  MediaType.IMAGE,
    "bmp":  MediaType.IMAGE,
    "tiff": MediaType.IMAGE,
    # Video
    "mp4":  MediaType.VIDEO,
    "avi":  MediaType.VIDEO,
    "mkv":  MediaType.VIDEO,
    "mov":  MediaType.VIDEO,
    "wmv":  MediaType.VIDEO,
    "flv":  MediaType.VIDEO,
    # Audio
    "mp3":  MediaType.AUDIO,
    "wav":  MediaType.AUDIO,
    "flac": MediaType.AUDIO,
    "aac":  MediaType.AUDIO,
    "ogg":  MediaType.AUDIO,
    "m4a":  MediaType.AUDIO,
    # Documents
    "pdf":  MediaType.DOCUMENT,
    "docx": MediaType.DOCUMENT,
    "txt":  MediaType.DOCUMENT,
}


@dataclass(frozen=True)
class ConversionRoute:
    """A single supported conversion from one format to another."""
    source_format: str          # e.g. "heic"
    target_format: str          # e.g. "jpg"
    converter_class: type[BaseConverter]
    lossy: bool = False         # Warn user if True


class ConversionRegistry:
    """Holds all registered conversion routes and validates requests."""

    def __init__(self) -> None:
        self._routes: dict[tuple[str, str], ConversionRoute] = {}

    def register(self, route: ConversionRoute) -> None:
        """Register a conversion route.

        Args:
            route: The ConversionRoute to register.
        """
        key = (route.source_format.lower(), route.target_format.lower())
        self._routes[key] = route

    def is_valid(self, source_format: str, target_format: str) -> bool:
        """Check if a conversion route exists.

        Args:
            source_format: Source extension without dot.
            target_format: Target extension without dot.

        Returns:
            True if the route is registered.
        """
        return (source_format.lower(), target_format.lower()) in self._routes

    def get_route(self, source_format: str, target_format: str) -> ConversionRoute:
        """Retrieve a registered route.

        Args:
            source_format: Source extension without dot.
            target_format: Target extension without dot.

        Returns:
            The matching ConversionRoute.

        Raises:
            ValueError: If no route is registered for this combination.
        """
        key = (source_format.lower(), target_format.lower())

        if key not in self._routes:
            src_type = EXTENSION_MEDIA_TYPE.get(source_format.lower())
            tgt_type = EXTENSION_MEDIA_TYPE.get(target_format.lower())

            if src_type and tgt_type and src_type != tgt_type:
                raise ValueError(
                    f"Cross-domain conversion not supported: "
                    f"{source_format} ({src_type.value}) → "
                    f"{target_format} ({tgt_type.value})"
                )

            raise ValueError(
                f"No conversion route registered for: "
                f"{source_format} → {target_format}"
            )

        return self._routes[key]

    def get_valid_targets(self, source_format: str) -> list[str]:
        """Return all valid target formats for a given source format.

        Args:
            source_format: Source extension without dot.

        Returns:
            Sorted list of valid target extensions.
        """
        src = source_format.lower()
        return sorted(
            target for (source, target) in self._routes if source == src
        )

    def get_media_type(self, extension: str) -> MediaType | None:
        """Return the MediaType for a given file extension.

        Args:
            extension: File extension without dot.

        Returns:
            MediaType or None if unknown.
        """
        return EXTENSION_MEDIA_TYPE.get(extension.lower())


def build_default_registry() -> ConversionRegistry:
    """Build and return the default registry with all supported routes.

    Returns:
        Fully populated ConversionRegistry.
    """
    registry = ConversionRegistry()

    image_routes = [
        ("heic", "jpg",  True),
        ("heic", "png",  False),
        ("jpg",  "png",  False),
        ("jpg",  "webp", True),
        ("png",  "jpg",  True),
        ("png",  "webp", False),
        ("png",  "gif",  False),
        ("webp", "jpg",  True),
        ("webp", "png",  False),
        ("gif",  "png",  False),
        ("bmp",  "jpg",  True),
        ("bmp",  "png",  False),
        ("tiff", "jpg",  True),
        ("tiff", "png",  False),
    ]

    video_routes = [
        ("mp4", "avi",  False),
        ("mp4", "mkv",  False),
        ("mp4", "mov",  False),
        ("avi", "mp4",  False),
        ("avi", "mkv",  False),
        ("mkv", "mp4",  False),
        ("mkv", "avi",  False),
        ("mov", "mp4",  False),
        ("mov", "avi",  False),
    ]

    audio_routes = [
        ("mp3",  "wav",  False),
        ("mp3",  "flac", False),
        ("wav",  "mp3",  True),
        ("wav",  "flac", False),
        ("flac", "mp3",  True),
        ("flac", "wav",  False),
        ("aac",  "mp3",  True),
        ("aac",  "wav",  False),
        ("m4a",  "mp3",  True),
        ("m4a",  "wav",  False),
    ]

    document_routes = [
        ("pdf",  "txt", False),
        ("docx", "txt", False),
    ]

    for src, tgt, lossy in image_routes:
        registry.register(ConversionRoute(src, tgt, ImageConverter, lossy))

    for src, tgt, lossy in video_routes:
        registry.register(ConversionRoute(src, tgt, VideoConverter, lossy))

    for src, tgt, lossy in audio_routes:
        registry.register(ConversionRoute(src, tgt, AudioConverter, lossy))

    for src, tgt, lossy in document_routes:
        registry.register(ConversionRoute(src, tgt, DocumentConverter, lossy))

    return registry


# Module-level singleton — import this everywhere
registry = build_default_registry()
