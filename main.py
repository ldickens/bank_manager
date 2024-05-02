from app import App
from presenter import Presenter
from rest_api import Model


def main() -> None:
    model = Model()
    presenter = Presenter(model)
    presenter.run()


main()
