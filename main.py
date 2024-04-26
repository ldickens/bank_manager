from app import App
from presenter import Presenter
from rest_api import Model


def main() -> None:
    model = Model()
    view = App()
    presenter = Presenter(view, model)
    presenter.run()


main()
