from paraview import simple, servermanager
from trame.decorators import change
from trame.widgets import html, client
from trame.widgets import vuetify3 as v3
from paraview.modules.vtkRemotingServerManager import vtkSMInputArrayDomain

PXM = servermanager.ProxyManager()
READERS = []
ALL_SOURCES = [
    (item["group"], item["key"]) for item in PXM.NewDefinitionIterator("sources")
]
FILTERS = [
    (item["group"], item["key"]) for item in PXM.NewDefinitionIterator("filters")
]
for group, name in ALL_SOURCES:
    hints = PXM.GetProxyHints(group, name)
    if hints is None:
        continue

    if hints.FindNestedElementByName("ReaderFactory"):
        READERS.append((group, name))

SOURCES = sorted(list(set(ALL_SOURCES) - set(READERS)), key=lambda x: x[1])


def to_reason(domain):
    if domain.IsA("vtkSMDataTypeDomain"):
        return domain.GetDomainDescription()
    if domain.IsA("vtkSMInputArrayDomain"):
        reasons = []
        if domain.GetAttributeType() == vtkSMInputArrayDomain.ANY:
            reasons.append("Requires an attribute array")
        else:
            reasons.append(
                f"Requires a {domain.GetAttributeTypeAsString()} attribute array"
            )

        components = list(domain.GetAcceptableNumbersOfComponents())
        if len(components):
            last = components.pop(-1)
            for comp in enumerate(components):
                reasons.append(f"with {comp} component(s) or ")
            reasons.append(f"with {last} component(s)")

        return " ".join(reasons)

    return "Requirements not met"


def to_item(group, name, inputs):
    proto_proxy = PXM.GetPrototypeProxy(group, name)
    input_prop = proto_proxy.GetProperty("Input")
    if input_prop is None:
        return {
            "group": group,
            "name": name,
            "available": True,  # sources are always available
        }

    if not input_prop.GetMultipleInput() and len(inputs) > 1:
        return {
            "group": group,
            "name": name,
            "available": False,
            "reason": f"Expect several input, but {len(inputs)} provided",
        }

    result_item = {
        "group": group,
        "name": name,
        "available": False,
        "reason": f"Expect several input, but {len(inputs)} provided",
    }

    input_prop.RemoveAllUncheckedProxies()
    for input in inputs:
        # TODO support non zero output ports
        input_prop.AddUncheckedInputConnection(input.SMProxy, 0)

    # Update item
    result_item["available"] = input_prop.IsInDomains()
    if not result_item["available"]:
        domain_iter = input_prop.NewDomainIterator()
        domain_iter.Begin()
        while not domain_iter.IsAtEnd():
            domain = domain_iter.GetDomain()
            domain_iter.Next()
            if not domain.IsInDomain(input_prop):
                result_item["reason"] = to_reason(domain)

    input_prop.RemoveAllUncheckedProxies()

    return result_item


class AddFilterDialog(v3.VDialog):
    def __init__(self, show_dialog=False, **_):
        super().__init__(v_model=("ptc_filter_dialog_open", show_dialog))
        self.pxm = servermanager.ProxyManager()

        # Default state
        self.state.setdefault("ptc_filter_active", None)
        self.state.setdefault("ptc_filter_list", [])
        self.state.setdefault("ptc_filter_offset", 0)
        self.refresh_filters()

        # Connect filter update
        self.ctrl.on_active_proxy_change.add(self.refresh_filters)

        # Define UI
        with self, v3.VCard(classes="w-50 mx-auto pa-2"):
            client.ClientStateChange(
                value="ptc_filter_active",
                change="utils.get('document').querySelector('.ptc-active-filter')?.scrollIntoView({ inline: 'nearest' })",
            )

            v3.VTextField(
                v_model=("ptc_filter_search", ""),
                variant="outlined",
                hide_details=True,
                density="compact",
                autofocus=True,
                enter=(self.create_filter, "[ptc_filter_active]"),
                up="ptc_filter_offset--",
                down="ptc_filter_offset++",
                __events=[
                    ("enter", "keyup.enter"),
                    ("up", "keyup.up"),
                    ("down", "keyup.down"),
                ],
            )
            with v3.VTable(
                height="30vh", classes="my-2 border-thin", density="compact", hover=True
            ):
                with html.Tbody():
                    with html.Template(
                        v_for="entry, idx in ptc_filter_list",
                        key="idx",
                    ):
                        with html.Tr(
                            v_show="entry.name.toLowerCase().includes(ptc_filter_search) && (!ptc_filter_hide_unavailable || entry.available)",
                            style=(
                                "`cursor: ${entry.available ? 'pointer' : 'not-allowed'}`",
                            ),
                            classes=(
                                "`${entry.name === ptc_filter_active?.name ? 'bg-primary ptc-active-filter' : ''}`",
                            ),
                        ):
                            with html.Td(classes="px-1"):
                                v3.VIcon(
                                    "mdi-check", color="green", v_if="entry.available"
                                )
                                v3.VIcon("mdi-alert-outline", color="red", v_else=True)
                            with html.Td(
                                "{{ entry.name }}",
                                click=(self.create_filter, "[entry]"),
                                classes="w-100 px-1",
                            ):
                                v3.VTooltip(
                                    "{{ entry.reason }}",
                                    activator="parent",
                                    location="bottom",
                                    v_if="!entry.available",
                                )
            v3.VCheckbox(
                v_model=("ptc_filter_hide_unavailable", True),
                density="compact",
                hide_details=True,
                label="Hide unavailable filters",
            )

    def create_filter(self, filter):
        if not filter.get("available"):
            return

        self.state.ptc_filter_search = ""
        self.state.ptc_filter_dialog_open = False

        proxy_group = filter.get("group")
        proxy_name = filter.get("name")
        proxy = servermanager._getPyProxy(PXM.NewProxy(proxy_group, proxy_name))
        controller = servermanager.ParaViewPipelineController()
        controller.PreInitializeProxy(proxy)

        inputName = servermanager.vtkSMCoreUtilities.GetInputPropertyName(
            proxy.SMProxy, 0
        )
        active_objects = simple.active_objects
        if inputName is not None:
            if (
                proxy.GetProperty(inputName).GetRepeatable()
                and active_objects.get_selected_sources()
            ):
                proxy.SetPropertyWithName(
                    inputName, active_objects.get_selected_sources()
                )
            elif active_objects.source:
                proxy.SetPropertyWithName(inputName, active_objects.source)

        controller.PostInitializeProxy(proxy)
        controller.RegisterPipelineProxy(proxy, proxy_name)
        simple.SetActiveSource(proxy)
        simple.Show()

        self.server.controller.on_active_proxy_change()
        self.server.controller.on_data_loaded()
        self.server.controller.on_data_change()

    @change("ptc_filter_search", "ptc_filter_list", "ptc_filter_offset")
    def on_search(self, ptc_filter_search, ptc_filter_list, ptc_filter_offset, **_):
        search_query = ptc_filter_search.lower()
        available_results = []
        for item in ptc_filter_list:
            name = item.get("name").lower()

            if not item.get("available"):
                continue

            if search_query in name:
                available_results.append(item)

        if 0 <= ptc_filter_offset < len(available_results):
            self.state.ptc_filter_active = available_results[ptc_filter_offset]
        elif available_results:
            self.state.ptc_filter_offset = max(
                0, min(ptc_filter_offset, len(available_results) - 1)
            )
            self.state.ptc_filter_active = available_results[
                self.state.ptc_filter_offset
            ]
        else:
            self.state.ptc_filter_active = None

    @change("ptc_filter_dialog_open")
    def on_visibility_change(self, ptc_filter_dialog_open, **_):
        if ptc_filter_dialog_open:
            self.refresh_filters()

    def refresh_filters(self):
        if not self.state.ptc_filter_dialog_open:
            return

        inputs = []
        if simple.GetActiveSource() is not None:
            inputs.append(simple.GetActiveSource())

        self.state.ptc_filter_list = [
            *[to_item(s[0], s[1], inputs) for s in SOURCES],
            *[to_item(s[0], s[1], inputs) for s in FILTERS],
        ]

        self.state.ptc_filter_active = self.state.ptc_filter_list[0]
