import io

import typer
from PIL import Image


def fill_code(img_resp: bytes, manual: bool = True) -> str:
    if manual:
        typer.secho(f"Please enter the verification code: ", fg=typer.colors.BRIGHT_YELLOW)
        with Image.open(io.BytesIO(img_resp)) as image:
            image.show()
            return input()
    else:
        # Implement image recognition here by yourself
        return ""
