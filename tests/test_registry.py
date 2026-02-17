"""Tests for the conversion registry."""

import pytest

from src.registry import build_default_registry, ConversionRoute, MediaType
from src.converters.image import ImageConverter


class TestConversionRegistry:
    """Tests for ConversionRegistry."""

    def setup_method(self) -> None:
        self.registry = build_default_registry()

    def test_valid_image_conversion(self) -> None:
        assert self.registry.is_valid("heic", "jpg") is True

    def test_valid_video_conversion(self) -> None:
        assert self.registry.is_valid("mp4", "avi") is True

    def test_valid_audio_conversion(self) -> None:
        assert self.registry.is_valid("wav", "mp3") is True

    def test_valid_document_conversion(self) -> None:
        assert self.registry.is_valid("pdf", "txt") is True

    def test_invalid_cross_domain_raises(self) -> None:
        with pytest.raises(ValueError, match="Cross-domain"):
            self.registry.get_route("mp4", "pdf")

    def test_invalid_route_raises(self) -> None:
        with pytest.raises(ValueError):
            self.registry.get_route("heic", "mp3")

    def test_get_valid_targets(self) -> None:
        targets = self.registry.get_valid_targets("heic")
        assert "jpg" in targets
        assert "png" in targets
        assert "mp4" not in targets

    def test_case_insensitive(self) -> None:
        assert self.registry.is_valid("HEIC", "JPG") is True
        assert self.registry.is_valid("Heic", "Jpg") is True

    def test_get_media_type_image(self) -> None:
        assert self.registry.get_media_type("jpg") == MediaType.IMAGE

    def test_get_media_type_video(self) -> None:
        assert self.registry.get_media_type("mp4") == MediaType.VIDEO

    def test_get_media_type_unknown(self) -> None:
        assert self.registry.get_media_type("xyz") is None

    def test_lossy_flag_on_route(self) -> None:
        route = self.registry.get_route("heic", "jpg")
        assert route.lossy is True

    def test_lossless_flag_on_route(self) -> None:
        route = self.registry.get_route("heic", "png")
        assert route.lossy is False

    def test_correct_converter_class(self) -> None:
        route = self.registry.get_route("png", "jpg")
        assert route.converter_class is ImageConverter
