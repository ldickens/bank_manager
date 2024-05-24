import sys

from app import App
from presenter import Presenter
from rest_api import Model


def main() -> None:
    model = Model()
    presenter = Presenter(model)
    presenter.run()

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        print("running in a PyInstaller bundle")
    else:
        print("running in a normal Python process")


main()
