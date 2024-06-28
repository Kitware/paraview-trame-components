from dataclasses import dataclass
from vtkmodules.vtkCommonDataModel import vtkDataAssembly
from trame.widgets import vuetify3
from paraview import simple

vuetify3.enable_lab()


@dataclass
class TreeNode:
    id: int
    title: str
    children: list

    @property
    def json(self):
        if self.children:
            return dict(
                value=self.id,
                title=self.title,
                children=[c.json for c in self.children],
            )
        return dict(value=self.id, title=self.title)


def get_node(assembly, node_id):
    node_name = assembly.GetNodeName(node_id)
    children = []
    for child_id in assembly.GetChildNodes(node_id, False, vtkDataAssembly.DepthFirst):
        children.append(get_node(assembly, child_id))

    return TreeNode(node_id, node_name, children if len(children) else None)


def proxy_to_tree(proxy):
    proxy.UpdatePipeline()
    data_info = proxy.GetDataInformation()
    assembly = data_info.GetDataAssembly()
    if assembly is None:
        assembly = data_info.GetHierarchy()
    return assemby_to_tree(assembly)


def assemby_to_tree(assembly):
    return get_node(assembly, 0).json


class MultiBlockInspector(vuetify3.VTreeview):
    def __init__(self, listen_to_active=True, proxy=None, **kwargs):
        super().__init__(
            items=("multiblock_tree", []),
            **{
                "activatable": True,
                "active_strategy": "classic",
                "v_model_activated": ("multiblock_active", []),
                "density": "compact",
                **kwargs,
            },
        )
        self._attr_names += [("v_model_activated", "v-model:activated")]
        self._proxy = None
        self.listen_to_active = listen_to_active
        self.ctrl.on_active_proxy_change.add(self.on_active_change)
        self.ctrl.on_server_ready.add(self.on_active_change)
        self.state.change("multiblock_active")(self.on_selection_change)
        self.set_source_proxy(proxy)

    @property
    def source_proxy(self):
        return self._proxy

    def set_source_proxy(self, v):
        self._proxy = v
        if v is None:
            self.state.multiblock_tree = []
        else:
            self.state.multiblock_tree = proxy_to_tree(v).get("children", [])

    def on_active_change(self, **_):
        if self.listen_to_active:
            self.set_source_proxy(simple.GetActiveSource())

    def on_selection_change(self, multiblock_active, **_):
        print("active node", multiblock_active)
