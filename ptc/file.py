import re
from pathlib import Path

from paraview import simple
from trame.decorators import TrameApp, change
from trame.widgets import html
from trame.widgets import vuetify3 as v3

# -----------------------------------------------------------------------------
# Utils
# -----------------------------------------------------------------------------

DIRECTORY = dict(icon="mdi-folder", type="directory")
GROUP = dict(icon="mdi-file-document-multiple-outline", type="group")
FILE = dict(icon="mdi-file-document-outline", type="file")

HEADERS = [
    {"title": "Name", "align": "start", "key": "name", "sortable": False},
    {"title": "Size", "align": "end", "key": "size", "sortable": False},
    {"title": "Date", "align": "end", "key": "modified", "sortable": False},
]


def sort_by_name(e):
    return e.get("name")


def to_type(e):
    return e.get("type", "")


def to_suffix(e):
    return Path(e.get("name", "")).suffix


# -----------------------------------------------------------------------------


class FileBrowser:
    def __init__(self, home=None, current=None):
        self._enable_groups = True
        self._home_path = Path(home).resolve() if home else Path.home()
        self._current_path = Path(current).resolve() if current else self._home_path

    @property
    def enable_groups(self):
        return self._enable_groups

    @enable_groups.setter
    def enable_groups(self, v):
        self._enable_groups = v

    @property
    def listing(self):
        directories = []
        files = []
        for f in self._current_path.iterdir():
            if f.name[0] == ".":
                continue
            entry = dict(name=f.name, modified=f.stat().st_mtime)
            if f.is_dir():
                directories.append({**entry, **DIRECTORY})
            elif f.is_file():
                files.append({**entry, **FILE, "size": f.stat().st_size})

        # Sort content
        directories.sort(key=sort_by_name)
        files.sort(key=sort_by_name)

        return [{**e, "index": i} for i, e in enumerate([*directories, *files])]

    def open_entry(self, entry):
        entry_type = entry.get("type")
        if entry_type in ["directory", "file"]:
            self._current_path = self._current_path / entry.get("name")
            return entry_type, str(self._current_path)
        if entry_type == "group":
            files = entry.get("files", [])
            return entry, [str(self._current_path / f) for f in files]
        return None

    def goto_home(self):
        self._current_path = self._home_path

    def goto_parent(self):
        self._current_path = self._current_path.parent

    def open_dataset(self, entry):
        return self._current_path / entry.get("name")

    def open_state(self, entry):
        return self._current_path / entry.get("name")


# -----------------------------------------------------------------------------


class ParaViewFileBrowser:
    def __init__(
        self,
        home=None,
        current=None,
        exclude=r"^\.|~$|^\$",
        group=r"[0-9]+\.",
    ):
        self._enable_groups = True
        self._home_path = Path(home).resolve() if home else Path.home()
        self._current_path = Path(current).resolve() if current else self._home_path
        self.pattern_exclude = re.compile(exclude)
        self.pattern_group = re.compile(group)

        self._pxm = simple.servermanager.ProxyManager()
        self._proxy_listing = self._pxm.NewProxy("misc", "ListDirectory")
        self._proxy_directories = simple.servermanager.VectorProperty(
            self._proxy_listing, self._proxy_listing.GetProperty("DirectoryList")
        )
        self._proxy_files = simple.servermanager.VectorProperty(
            self._proxy_listing, self._proxy_listing.GetProperty("FileList")
        )

    @property
    def enable_groups(self):
        return self._enable_groups

    @enable_groups.setter
    def enable_groups(self, v):
        self._enable_groups = v

    @property
    def listing(self):
        directories = []
        files = []
        groups = []
        g_map = {}

        self._proxy_listing.List(str(self._current_path.resolve()))
        self._proxy_listing.UpdatePropertyInformation()

        # Files + Groups
        file_listing = []
        if len(self._proxy_files) > 1:
            file_listing = self._proxy_files.GetData()
        if len(self._proxy_files) == 1:
            file_listing.append(self._proxy_files.GetData())
        file_listing = [
            file_name
            for file_name in file_listing
            if not re.search(self.pattern_exclude, file_name)
        ]
        for file_name in file_listing:
            f = self._current_path / file_name
            stats = f.stat()

            # Group or file?
            file_split = re.split(self.pattern_group, file_name)
            if self.enable_groups and len(file_split) == 2:
                # Group
                g_name = "*.".join(file_split)
                if g_name not in g_map:
                    g_entry = dict(
                        name=g_name,
                        modified=stats.st_mtime,
                        size=0,
                        files=[],
                        **GROUP,
                    )
                    g_map[g_name] = g_entry
                    groups.append(g_entry)

                g_map[g_name]["size"] += stats.st_size
                g_map[g_name]["files"].append(file_name)
                # Many need to sort files???
            else:
                # File
                files.append(
                    dict(
                        name=f.name,
                        modified=stats.st_mtime,
                        size=stats.st_size,
                        **FILE,
                    )
                )

        # Directories
        dir_listing = []
        if len(self._proxy_directories) > 1:
            dir_listing = self._proxy_directories.GetData()
        if len(self._proxy_directories) == 1:
            dir_listing.append(self._proxy_directories.GetData())
        dir_listing = [
            dir_name
            for dir_name in dir_listing
            if not re.search(self.pattern_exclude, dir_name)
        ]
        for dir_name in dir_listing:
            f = self._current_path / dir_name
            directories.append(
                dict(name=f.name, modified=f.stat().st_mtime, **DIRECTORY)
            )

        # Sort content
        directories.sort(key=sort_by_name)
        groups.sort(key=sort_by_name)
        files.sort(key=sort_by_name)

        return [
            {**e, "index": i} for i, e in enumerate([*directories, *groups, *files])
        ]

    def open_entry(self, entry):
        entry_type = entry.get("type")
        if entry_type in ["directory", "file"]:
            self._current_path = self._current_path / entry.get("name")
            return entry_type, str(self._current_path)
        if entry_type == "group":
            files = entry.get("files", [])
            return entry, [str(self._current_path / f) for f in files]
        return None

    def goto_home(self):
        self._current_path = self._home_path

    def goto_parent(self):
        self._current_path = self._current_path.parent

    def open_dataset(self, entry):
        event = {}
        if to_type(entry) == "group":
            files = [str(self._current_path / f) for f in entry.get("files")]
            source = simple.OpenDataFile(files)
            representation = simple.Show(source)
            view = simple.Render()
            event = dict(
                source=source, representation=representation, view=view, type="group"
            )
        else:
            source = simple.OpenDataFile(str(self._current_path / entry.get("name")))
            representation = simple.Show(source)
            view = simple.Render()
            event = dict(
                source=source, representation=representation, view=view, type="dataset"
            )

        return event

    def open_state(self, entry):
        state_file = str(self._current_path / entry.get("name"))
        simple.LoadState(state_file)
        view = simple.Render()
        return dict(type="state", view=view, state_file=state_file)


# -----------------------------------------------------------------------------
# GUI Components
# -----------------------------------------------------------------------------


@TrameApp()
class OpenFileDialog(v3.VDialog):
    def __init__(
        self,
        file_browser=None,
        dialog_open=True,
        open_state_available=True,
        state_file_extensions=None,
        **_,
    ):
        super().__init__(v_model=("ptc_openfile_dialog_open", dialog_open))

        # State file extensions
        if state_file_extensions is None:
            state_file_extensions = [".pvsm", ".png"]
        self._state_file_extensions = state_file_extensions

        # Initialize file browser
        if file_browser is None:
            file_browser = ParaViewFileBrowser()
        self._file_browser = file_browser

        # Fill content for home
        self.goto_home()
        self.selected_entry = None

        # Define UI
        with self, v3.VCard(classes="mx-10"):
            style_align_center = "d-flex align-center "
            v3.VCardTitle("Open File", classes="text-center bg-grey-lighten-2")
            with v3.VToolbar(density="compact", color="white"):
                v3.VBtn(
                    icon="mdi-home",
                    variant="flat",
                    size="small",
                    click=self.goto_home,
                )
                v3.VBtn(
                    icon="mdi-folder-upload-outline",
                    variant="flat",
                    size="small",
                    click=self.goto_parent,
                )
                v3.VTextField(
                    v_model=("ptc_openfile_filter", ""),
                    hide_details=True,
                    color="primary",
                    placeholder="filter",
                    density="compact",
                    variant="outlined",
                    classes="mx-2",
                    prepend_inner_icon="mdi-magnify",
                    clearable=True,
                )
            with v3.VDataTable(
                density="compact",
                fixed_header=True,
                headers=("ptc_openfile_headers", HEADERS),
                items=("ptc_openfile_listing", []),
                height="50vh",
                style="user-select: none; cursor: pointer;",
                hover=True,
                search=("ptc_openfile_filter",),
                items_per_page=-1,
            ):
                v3.Template(raw_attrs=["v-slot:bottom"])
                with v3.Template(raw_attrs=['v-slot:item="{ index, item }"']):
                    with v3.VDataTableRow(
                        index=("index",),
                        item=("item",),
                        click=(self.select_entry, "[item]"),
                        dblclick=(self.open_entry, "[item]"),
                        classes=(
                            "{ 'bg-grey': item.index === ptc_openfile_active, 'cursor-pointer': 1 }",
                        ),
                    ):
                        with v3.Template(raw_attrs=["v-slot:item.name"]):
                            with html.Div(classes=style_align_center):
                                v3.VIcon(
                                    "{{ item.icon }}",
                                    size="small",
                                    classes="mr-2",
                                )
                                html.Div("{{ item.name }}")

                        with v3.Template(raw_attrs=["v-slot:item.size"]):
                            with html.Div(
                                classes=style_align_center + " justify-end",
                            ):
                                html.Div(
                                    "{{ utils.fmt.bytes(item.size, 0) }}",
                                    v_if="item.size",
                                )
                                html.Div(" - ", v_else=True)

                        with v3.Template(raw_attrs=["v-slot:item.modified"]):
                            with html.Div(
                                classes=style_align_center + " justify-end",
                            ):
                                html.Div(
                                    "{{ new Date(item.modified * 1000).toDateString() }}"
                                )

            with v3.VCardActions():
                v3.VCheckbox(
                    v_model=("ptc_openfile_groups", True),
                    density="compact",
                    hide_details=True,
                    false_icon="mdi-file-document-outline",
                    true_icon="mdi-file-document-multiple-outline",
                    label=(
                        "` Groups ${ptc_openfile_groups ? 'enabled' : 'disabled'}`",
                    ),
                    classes="mx-2",
                )
                v3.VSpacer()
                if open_state_available:
                    v3.VBtn(
                        "Open State",
                        variant="tonal",
                        disabled=("ptc_openfile_state_disabled", True),
                        click=(
                            self.open_state,
                            "[ptc_openfile_listing[ptc_openfile_active]]",
                        ),
                    )
                v3.VBtn(
                    "Open DataSet",
                    variant="tonal",
                    disabled=("ptc_openfile_dataset_disabled", True),
                    click=(
                        self.open_dataset,
                        "[ptc_openfile_listing[ptc_openfile_active]]",
                    ),
                )
                v3.VBtn(
                    "Cancel", variant="tonal", click="ptc_openfile_dialog_open = false"
                )

    @property
    def state(self):
        return self.server.state

    def _update_listing(self):
        self.selected_entry = None
        self.state.ptc_openfile_active = -1
        self.state.ptc_openfile_listing = self._file_browser.listing

    def goto_home(self):
        self._file_browser.goto_home()
        self._update_listing()

    def goto_parent(self):
        self._file_browser.goto_parent()
        self._update_listing()

    def select_entry(self, entry):
        self.selected_entry = entry
        self.state.ptc_openfile_active = entry.get("index", 0) if entry else -1
        self.ptc_openfile_dataset_disabled = True
        self.state.ptc_openfile_state_disabled = True

        # Update button state
        if entry and to_type(entry) in ["file", "group"]:
            self.state.ptc_openfile_dataset_disabled = False

        if entry and to_suffix(entry) in self._state_file_extensions:
            self.state.ptc_openfile_state_disabled = False

    def open_entry(self, entry):
        if to_type(entry) == "directory":
            self._file_browser.open_entry(entry)
            self._update_listing()
        else:
            self.open_dataset(entry)

    def open_dataset(self, entry):
        self.state.ptc_openfile_dialog_open = False
        event = self._file_browser.open_dataset(entry)
        if self.server.controller.on_file_open.exists():
            self.server.controller.on_file_open(event)

        self.server.controller.on_data_loaded()
        self.server.controller.on_data_change()
        self.server.controller.on_active_proxy_change()
        self.server.controller.view_update()

    def open_state(self, entry):
        self.state.ptc_openfile_dialog_open = False
        self._file_browser.open_state(entry)
        self.server.controller.on_data_loaded()
        self.server.controller.on_data_change()
        self.server.controller.on_active_proxy_change()
        simple.GetActiveView().MakeRenderWindowInteractor(True)

    @change("ptc_openfile_groups")
    def on_enable_group_change(self, ptc_openfile_groups, **_):
        self._file_browser.enable_groups = ptc_openfile_groups
        self._update_listing()


class OpenFileToggle(v3.VBtn):
    def __init__(self, **kwargs):
        super().__init__(
            icon="mdi-file-document-plus-outline",
            click="ptc_openfile_dialog_open = !ptc_openfile_dialog_open",
            **kwargs,
        )
        self.dialog = OpenFileDialog(dialog_open=False)
