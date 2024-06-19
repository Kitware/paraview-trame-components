from trame.widgets.html import Div


def col_left():
    return Div(
        classes="d-flex flex-column align-start ptc-region ptc-over",
        style="position: absolute; top: 1rem; bottom: 1rem; left: 1rem; width: calc(33vw - 0.5rem);",
    )


def col_center():
    return Div(
        classes="d-flex flex-column align-center justify-space-between ptc-region ptc-over",
        style="position: absolute; top: 1rem; bottom: 1rem; left: 50%; width: calc(33vw - 0.5rem); transform: translateX(-50%);",
    )


def col_right():
    return Div(
        classes="d-flex flex-column align-end ptc-region ptc-over",
        style="position: absolute; bottom: 1rem; top: 1rem; right: 1rem; width: calc(33vw - 0.5rem);",
    )


FN_MAPPING = dict(col_left=col_left, col_center=col_center, col_right=col_right)


class ColumnsManager:
    def handle(self, name):
        if name in FN_MAPPING:
            return self
        return None

    def create_container(self, name):
        return FN_MAPPING.get(name)()
