from trame.widgets.html import Div


def col_left():
    return Div(
        classes="d-flex flex-column align-start ",
        style="position: absolute; top: 1rem; bottom: 1rem; left: 1rem; width: calc(33vw - 0.5rem); z-index: 1; pointer-events: none;",
    )


def col_center():
    return Div(
        classes="d-flex flex-column align-center justify-space-between ",
        style="position: absolute; top: 1rem; bottom: 1rem; left: 50%; width: calc(33vw - 0.5rem); z-index: 1; transform: translateX(-50%); pointer-events: none;",
    )


def col_right():
    return Div(
        classes="d-flex flex-column align-end ",
        style="position: absolute; bottom: 1rem; top: 1rem; right: 1rem; width: calc(33vw - 0.5rem); z-index: 1; pointer-events: none;",
    )


FN_MAPPING = dict(col_left=col_left, col_center=col_center, col_right=col_right)


class ColumnsManager:
    def handle(self, name):
        if name in FN_MAPPING:
            return self
        return None

    def create_container(self, name):
        return FN_MAPPING.get(name)()
