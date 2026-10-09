"""The image filters that can be named in a JSON file."""

import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

from filtre_class import Filter
from image_io import load_image

def _check_image(image: Image.Image) -> None:
    if image.mode not in ("RGB", "RGBA"):
        raise ValueError("The image must be RGB or RGBA.")


def _check_intensity(value: float) -> None:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or not 0 <= value <= 100
    ):
        raise ValueError("Intensity must be between 0 and 100.")


class ContrastFilter(Filter):
    def __init__(self, intensity: float = 50):
        _check_intensity(intensity)
        self.intensity = intensity

    def apply(self, image: Image.Image) -> Image.Image:
        _check_image(image)

        alpha = image.getchannel("A") if image.mode == "RGBA" else None

        # 0 -> minimum, 50 -> original, 100 -> maximum
        factor = self.intensity / 50

        result = ImageEnhance.Contrast(
            image.convert("RGB")
        ).enhance(factor)

        if alpha is not None:
            result.putalpha(alpha)

        return result


class SaturationFilter(Filter):
    def __init__(self, intensity: float = 50):
        _check_intensity(intensity)
        self.intensity = intensity

    def apply(self, image: Image.Image) -> Image.Image:
        _check_image(image)

        alpha = image.getchannel("A") if image.mode == "RGBA" else None

        # 0 -> grayscale, 50 -> original, 100 -> maximum saturation
        factor = self.intensity / 50

        result = ImageEnhance.Color(
            image.convert("RGB")
        ).enhance(factor)

        if alpha is not None:
            result.putalpha(alpha)

        return result


class BlendFilter(Filter):
    def __init__(self, image2: str | Path, intensity: float = 50):
        _check_intensity(intensity)
        self.image2 = Path(image2)
        self.intensity = intensity

    def apply(self, image: Image.Image) -> Image.Image:
        _check_image(image)
        other = load_image(self.image2)
        if image.size != other.size:
            raise ValueError("Both images must have the same dimensions.")

        mode = (
            "RGBA"
            if "A" in image.getbands() or "A" in other.getbands()
            else "RGB"
        )
        return Image.blend(
            image.convert(mode),
            other.convert(mode),
            self.intensity / 100,
        )


class SplitBlendFilter(Filter):
    def __init__(self, image2: str | Path, intensity: float = 50):
        _check_intensity(intensity)
        self.image2 = Path(image2)
        self.intensity = intensity

    def apply(self, image: Image.Image) -> Image.Image:
        _check_image(image)
        other = load_image(self.image2)
        if image.size != other.size:
            raise ValueError("Both images must have the same dimensions.")

        mode = (
            "RGBA"
            if "A" in image.getbands() or "A" in other.getbands()
            else "RGB"
        )
        image1 = image.convert(mode)
        image2 = other.convert(mode)
        split_x = round(image.width * self.intensity / 100)

        result = Image.new(mode, image.size)
        result.paste(image1.crop((0, 0, split_x, image.height)), (0, 0))
        result.paste(
            image2.crop((split_x, 0, image.width, image.height)),
            (split_x, 0),
        )
        return result


class SelectiveColorFilter(Filter):
    def __init__(
        self,
        color: list[int] | tuple[int, int, int],
        intensity: float = 100,
    ):
        # Check that the selected color is a valid RGB color
        if (
            not isinstance(color, (list, tuple))
            or len(color) != 3
            or any(
                type(channel) is not int or not 0 <= channel <= 255
                for channel in color
            )
        ):
            raise ValueError("Color must be three RGB values from 0 to 255.")

        _check_intensity(intensity)

        self.color = tuple(color)
        self.intensity = intensity

    def apply(self, image: Image.Image) -> Image.Image:
        _check_image(image)

        rgb = image.convert("RGB")
        alpha = image.getchannel("A") if image.mode == "RGBA" else None

        # Create a grayscale version of the image
        gray = rgb.convert("L").convert("RGB")

        # Convert the 0-100 intensity to the 0-1 range used by Image.blend
        blend_intensity = self.intensity / 100

        # Make the non-selected part of the image grayscale
        result = Image.blend(rgb, gray, blend_intensity)

        # Convert to HSV to identify colors close to the selected color
        hue, saturation, _ = rgb.convert("HSV").split()

        selected_hue = (
            Image.new("RGB", (1, 1), self.color)
            .convert("HSV")
            .getpixel((0, 0))[0]
        )

        # Create a mask for pixels close to the selected hue
        hue_mask = hue.point(
            [
                255
                if min(
                    (value - selected_hue) % 256,
                    (selected_hue - value) % 256,
                )
                <= 12
                else 0
                for value in range(256)
            ]
        )

        color_mask = ImageChops.multiply(
            hue_mask,
            saturation.point(
                [255 if value >= 32 else 0 for value in range(256)]
            ),
        )

        # Keep the selected color in color
        result = Image.composite(rgb, result, color_mask)

        if alpha is not None:
            result.putalpha(alpha)

        return result


class CenterCircleFocusFilter(Filter):
    def __init__(self, intensity: float = 0, focus_size: float = 50):
        _check_intensity(intensity)

        if (
            isinstance(focus_size, bool)
            or not isinstance(focus_size, (int, float))
            or not math.isfinite(focus_size)
            or not 0 <= focus_size <= 100
        ):
            raise ValueError("Circle size must be between 0 and 100.")

        self.intensity = intensity
        self.focus_size = focus_size

    def apply(self, image: Image.Image) -> Image.Image:
        _check_image(image)

        rgb = image.convert("RGB")
        alpha = image.getchannel("A") if image.mode == "RGBA" else None

        # Convert intensity 0-100 to a Gaussian blur radius 0-10
        blur_radius = self.intensity / 10
        blurred = rgb.filter(ImageFilter.GaussianBlur(blur_radius))

        width, height = image.size

        # focus_size represents a percentage of the smallest image dimension
        diameter = int(min(width, height) * self.focus_size / 100)

        left = (width - diameter) // 2
        top = (height - diameter) // 2

        mask = Image.new("L", image.size, 0)

        if diameter > 0:
            ImageDraw.Draw(mask).ellipse(
                (left, top, left + diameter - 1, top + diameter - 1),
                fill=255,
            )

        # Keep the center sharp and blur the outside
        result = Image.composite(rgb, blurred, mask)

        if alpha is not None:
            result.putalpha(alpha)

        return result


FILTER_CLASSES = {
    "contrast": ContrastFilter,
    "saturation": SaturationFilter,
    "blend": BlendFilter,
    "splitblend": SplitBlendFilter,
    "selectivecolor": SelectiveColorFilter,
    "centercirclefocus": CenterCircleFocusFilter,
}