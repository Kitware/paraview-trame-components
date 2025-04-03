from paraview import servermanager, simple
from trame.widgets.trame import GitTree

PXM = servermanager.ProxyManager()


def id_to_proxy(_id):
    try:
        _id = int(_id)
    except ValueError:
        return None
    if _id <= 0:
        return None

    return simple.servermanager._getPyProxy(
        simple.servermanager.ActiveConnection.Session.GetRemoteObject(_id)
    )


class PipelineBrowser(GitTree):
    def __init__(self, width=200, **kwargs):
        super().__init__(
            sources=("pipeline_sources", []),
            actives=("pipeline_actives", []),
            width=width,
            # Events
            actives_change=(self.on_active_change, "[$event]"),
            visibility_change=(
                self.on_visibility_change,
                "[$event.id, $event.visible]",
            ),
            **{
                **kwargs,
                "classes": kwargs.get("classes", "elevation-5 rounded-lg"),
                "style": kwargs.get(
                    "style",
                    "pointer-events: auto; user-select: none; background: rgba(255, 255, 255, 0.5);",
                ),
            },
        )
        self._internal_proxies = set()
        self._deleted_ids = set()
        self.update()
        self.server.controller.on_active_view_change.add(self.update)
        self.server.controller.on_data_loaded.add(self.update)
        self.server.controller.on_data_change.add(self.update)
        self.server.controller.register_internal_proxy.add(self.register_internal_proxy)
        self.server.controller.on_active_proxy_change.add(self.update_active)

    def on_active_change(self, active_ids, **_):
        current_active = simple.GetActiveSource()
        proxy = None
        if len(active_ids):
            _id = active_ids[0]
            if _id in self._deleted_ids:
                return
            proxy = id_to_proxy(_id)

        if current_active == proxy:
            simple.SetActiveSource(None)
        else:
            simple.SetActiveSource(proxy)

        self.update_active()

        # Use life cycle handler
        if self.server.controller.on_active_proxy_change.exists():
            self.server.controller.on_active_proxy_change()

    def on_visibility_change(self, proxy_id, visible, **_):
        proxy = id_to_proxy(proxy_id)
        view_proxy = simple.GetActiveView()
        representation = simple.GetRepresentation(proxy=proxy, view=view_proxy)
        representation.Visibility = 1 if visible else 0

        # Use life cycle handler
        self.server.controller.on_data_change()

    def update_active(self, **_):
        actives = []
        active_proxy = simple.GetActiveSource()
        if active_proxy:
            actives.append(active_proxy.GetGlobalIDAsString())
        self.server.state.pipeline_actives = actives

    def register_internal_proxy(self, proxy):
        self._internal_proxies.add(proxy.GetGlobalIDAsString())

    def update_sources(self, **_):
        sources = []
        proxies = PXM.GetProxiesInGroup("sources")
        view_proxy = simple.GetActiveView()
        leaves = {key[1] for key in proxies}
        node_map = {}
        for key in proxies:
            proxy = proxies[key]

            source = {"parent": "0"}
            source["name"] = key[0]
            source["id"] = key[1]

            if key[1] in self._internal_proxies:
                continue

            representation = simple.GetRepresentation(proxy=proxy, view=view_proxy)
            if representation:
                source["rep"] = representation.GetGlobalIDAsString()
                source["visible"] = int(representation.Visibility)
            else:
                source["rep"] = 0
                source["visible"] = 0

            if hasattr(proxy, "Input") and proxy.Input:
                input_prop = proxy.Input
                if hasattr(input_prop, "GetNumberOfProxies"):
                    num_proxies = input_prop.GetNumberOfProxies()
                    if num_proxies > 1:
                        source["multiparent"] = num_proxies
                        for input_idx in range(num_proxies):
                            proxy_id = input_prop.GetProxy(
                                input_idx
                            ).GetGlobalIDAsString()
                            if input_idx == 0:
                                source["parent"] = proxy_id
                            else:
                                source[f"parent_{input_idx}"] = proxy_id
                    elif num_proxies == 1:
                        source["parent"] = input_prop.GetProxy(0).GetGlobalIDAsString()
                else:
                    source["parent"] = input_prop.GetGlobalIDAsString()

            sources.append(source)
            node_map[source["id"]] = source
            leaves.discard(source["parent"])

        self.server.state.pipeline_sources = sources

    def update(self, **_):
        self.update_sources()
        self.update_active()
