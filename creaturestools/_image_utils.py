from PIL import Image


def convert_image(img, mode, palette=None):
    if img.mode != mode:
        if img.mode != "RGB":
            if img.mode in ("BGR;15", "BGR;16"):
                img = Image.frombytes(
                    "RGB", (img.width, img.height), img.tobytes(), "raw", img.mode
                )
            else:
                img = img.convert("RGB")
        if mode == "P":
            palette_image = Image.new("P", (1, 1))
            palette_image.putpalette(palette)
            img = img.quantize(palette=palette_image)
        elif mode != "RGB":
            img = img.convert(mode)
    return img
