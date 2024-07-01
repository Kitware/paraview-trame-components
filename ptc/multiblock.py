from dataclasses import dataclass
from vtkmodules.vtkCommonDataModel import vtkDataAssembly
from trame.widgets import vuetify3
from paraview import simple

vuetify3.enable_lab()


@dataclass
class TreeNode:
    id: int
    title: str
    path: str
    children: list

    @property
    def json(self):
        if self.children:
            return dict(
                value=self.id,
                title=self.title,
                path=self.path,
                children=[c.json for c in self.children],
            )
        return dict(value=self.id, title=self.title, path=self.path)


def get_node(assembly, node_id):
    node_name = assembly.GetNodeName(node_id)
    node_path = assembly.GetNodePath(node_id)

    # Remove empty node
    if node_name == "Unnamed":
        return None

    children = []
    for child_id in assembly.GetChildNodes(node_id, False, vtkDataAssembly.DepthFirst):
        child = get_node(assembly, child_id)
        if child:
            children.append(child)

    # Remove lonely child
    if len(children) == 1 and children[0].children is None:
        children = []

    return TreeNode(node_id, node_name, node_path, children if len(children) else None)


def proxy_to_assembly(proxy):
    if proxy is None:
        return None
    proxy.UpdatePipeline()
    data_info = proxy.GetDataInformation()
    assembly = data_info.GetDataAssembly()
    if assembly is None:
        assembly = data_info.GetHierarchy()
    return assembly


def proxy_to_tree(proxy):
    if proxy is None:
        return {}
    assembly = proxy_to_assembly(proxy)
    return assemby_to_tree(assembly)


def assemby_to_tree(assembly):
    if assembly is None:
        return {}
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
        self._assembly = None
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
        self._assembly = proxy_to_assembly(v)
        if v is None:
            self.state.multiblock_tree = []
        else:
            self.state.multiblock_tree = assemby_to_tree(self._assembly).get(
                "children", []
            )

    def on_active_change(self, **_):
        if self.listen_to_active:
            self.set_source_proxy(simple.GetActiveSource())

    def on_selection_change(self, multiblock_active, **_):
        # print("active node", multiblock_active)
        if self._assembly and len(multiblock_active) == 1:
            block_path = self._assembly.GetNodePath(multiblock_active[0])
            rep = simple.GetRepresentation(self._proxy)
            rep.BlockColors = [
                block_path,
                "1.0",
                "0.0",
                "0.0",
            ]
            self.server.controller.on_data_change()
        elif self._proxy:
            rep = simple.GetRepresentation(self._proxy)
            rep.BlockColors = []
            self.server.controller.on_data_change()
