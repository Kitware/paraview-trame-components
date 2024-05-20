import asyncio

from paraview import simple
from trame.app import asynchronous
from trame.decorators import TrameApp, change, controller
from trame.widgets import html, vuetify3


@TrameApp()
class TimeControl(vuetify3.VCard):
    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(
            v_show="time_nb > 0",
            **{
                **kwargs,
                "classes": kwargs.get("classes", "pa-1 px-2 elevation-5 rounded-lg"),
                "style": "width: 100%; overflow: hidden; background: rgba(255, 255, 255, 0.5);"
                + kwargs.get("style", ""),
            },
        )

        self.state.setdefault("time_index", 0)
        self.state.setdefault("time_nb", 0)
        self.state.setdefault("time_value", 0)

        with (
            self,
            html.Div(
                classes="d-flex align-center",
                style="pointer-events: auto; user-select: none;",
            ),
        ):
            vuetify3.VBtn(
                icon="mdi-skip-previous",
                density="compact",
                flat=True,
                click=self.first,
                classes="mr-1",
            )
            vuetify3.VBtn(
                icon="mdi-chevron-left",
                density="compact",
                flat=True,
                click=self.previous,
                classes="mr-1",
            )
            vuetify3.VBtn(
                icon="mdi-play",
                density="compact",
                flat=True,
                classes="mr-1",
                click=self.play,
                v_show="!time_play",
            )
            vuetify3.VBtn(
                icon="mdi-stop",
                density="compact",
                flat=True,
                classes="mr-1",
                click=self.stop,
                v_show=("time_play", False),
            )
            vuetify3.VBtn(
                icon="mdi-chevron-right",
                density="compact",
                flat=True,
                click=self.next,
                classes="mr-1",
            )
            vuetify3.VBtn(
                icon="mdi-skip-next",
                density="compact",
                flat=True,
                click=self.last,
                classes="mr-1",
            )
            html.Div(
                "{{ time_value.toFixed(4) }}  - {{ time_index + 1 }} / {{ time_nb }}",
                classes="text-caption text-center",
                style="width: 10rem;",
            )
            vuetify3.VSlider(
                v_model=("time_index", 0),
                min=0,
                max=("time_nb - 1",),
                step=1,
                density="compact",
                hide_details=True,
            )

        self.update()

    @property
    def state(self):
        return self.server.state

    @property
    def time_values(self):
        return list(simple.GetTimeKeeper().TimestepValues)

    @change("time_index")
    @controller.add("on_data_loaded")
    def update(self, **_):
        time_values = self.time_values
        self.state.time_nb = len(time_values)
        if self.time_index >= self.state.time_nb:
            self.state.time_index = 0
        if self.time_index < 0:
            self.state.time_index = self.state.time_nb + self.time_index

        tk = simple.GetTimeKeeper()
        if len(time_values) < 1:
            self.state.time_value = 0
        else:
            self.state.time_value = time_values[self.state.time_index]
            tk.Time = self.state.time_value
            self.server.controller.on_data_change()

    @property
    def time_index(self):
        return self.state.time_index

    def first(self):
        self.state.time_index = 0

    def last(self):
        self.state.time_index = len(self.time_values) - 1

    def previous(self):
        self.state.time_index = self.time_index - 1

    def next(self):
        self.state.time_index = self.time_index + 1

    def play(self):
        if not self.state.play:
            self.state.time_play = True
            asynchronous.create_task(self.play_animation())

    def stop(self):
        self.state.time_play = False

    async def play_animation(self):
        with self.state:
            while self.state.time_play:
                with self.state:
                    self.next()
                await asyncio.sleep(0.1)
