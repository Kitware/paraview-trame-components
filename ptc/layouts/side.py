from trame.widgets import html


def side_left():
    return html.Div(
        classes="ptc-region",
        style="position: absolute; top: 1rem; bottom: 1rem; left: 1rem;",
    )


def side_right():
    return html.Div(
        classes="ptc-region",
        style="position: absolute; top: 1rem; bottom: 1rem; right: 1rem;",
    )


def side_bottom():
    return html.Div(
        classes="ptc-region",
        style="position: absolute; bottom: 1rem; left: 1rem; right: 1rem;",
    )


def side_top():
    return html.Div(
        classes="ptc-region",
        style="position: absolute; top: 1rem; left: 1rem; right: 1rem;",
    )


FN_MAPPING = dict(
    side_top=side_top,
    side_left=side_left,
    side_right=side_right,
    side_bottom=side_bottom,
)


class SideOverlayManager:
    def handle(self, name):
        if name in FN_MAPPING:
            return self
        return None

    def create_container(self, name):
        return FN_MAPPING.get(name)()
