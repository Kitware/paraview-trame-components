import ptc
from trame.app import TrameApp
from trame.ui.html import DivLayout
# from trame.widgets import html


class Demo(TrameApp):
    def __init__(self, server=None, **kwargs):
        super().__init__(server, **kwargs)
        self._build_ui()

    def _build_ui(self):
        with DivLayout(self.server) as self.ui:
            self.ui.root.style = (
                "position:absolute;left:0;top:0;height:100vh;width:100vw;"
            )
            ptc.MultiView(
                ctx_name="views",
                ready=lambda: self.ctx.views.add_view(),
            )


def main():
    app = Demo()
    app.server.start()


if __name__ == "__main__":
    main()
