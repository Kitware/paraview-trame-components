from paraview import simple
from trame.decorators import TrameApp, change
from trame.widgets import vuetify3 as v3


def s(v):
    if len(v) == 1:
        return v[0]
    return v


def is_sortable(array):
    return array.IsA("vtkDataArray") and array.GetNumberOfComponents() == 1


@TrameApp()
class ViewTable(v3.VCard):
    def __init__(
        self,
        source=None,
        **kwargs,
    ):
        self._source_proxy = source
        self._current_dataset = None
        self._current_block = None
        self._current_items = []
        self._current_headers = None
        self._current_page_slice = (0, 10)
        self._current_sort_mode = []

        super().__init__(
            **{
                **kwargs,
                "style": f"pointer-events: auto; overflow: auto; {kwargs.get('style')}",
            }
        )

        self.state.setdefault("view_table_multiblocks", [])

        with self:
            with v3.VCardTitle(v_show=("view_table_multiblock", False)):
                with v3.VTabs(v_model=("view_table_multiblock_active", None)):
                    v3.VTab(
                        "{{ block_name }}",
                        v_for="block_name, i in view_table_multiblocks",
                        key="i",
                    )

            v3.VDataTableServer(
                sticky=True,
                density="compact",
                fixed_header=True,
                fixed_footer=True,
                height="calc(100vh - 10rem)",
                headers=("view_table_headers", []),
                items=("view_table_items", []),
                items_length=("view_table_items_length", 0),
                items_value="index",
                v_model_items_per_page=("view_table_items_per_page", 10),
                update_options=(self.update_items, "[]", "$event"),
            )

    @property
    def state(self):
        return self.server.state

    @property
    def sorted_items(self):
        key = "index"
        reverse = False
        if len(self._current_sort_mode) == 1:
            key = self._current_sort_mode[0].get("key", "index")
            reverse = self._current_sort_mode[0].get("order", "asc") != "asc"

        self._current_items = sorted(
            self._current_items, key=lambda v: v.get(key), reverse=reverse
        )
        return self._current_items

    def load_data_from_proxy(self):
        self._current_dataset = simple.FetchData(self._source_proxy)

        if isinstance(self._current_dataset, dict) and len(self._current_dataset) == 1:
            self._current_dataset = next(iter(self._current_dataset.values()))

        if isinstance(self._current_dataset, dict):
            self.state.view_table_multiblock = len(self._current_dataset) > 1
            self.state.view_table_multiblocks = list(self._current_dataset.keys())
            self.state.view_table_multiblock_active = self.state.view_table_multiblocks[
                0
            ]
        if self._current_dataset.IsA("vtkPartitionedDataSetCollection"):
            n_partitions = self._current_dataset.GetNumberOfPartitionedDataSets()
            self.state.view_table_multiblock = n_partitions > 1
            self.state.view_table_multiblocks = list(range(n_partitions))
            self.state.view_table_multiblock_active = 0
        elif self._current_dataset.IsA("vtkPartitionedDataSet"):
            while self._current_dataset.GetNumberOfPartitions() == 1:
                self._current_dataset = self._current_dataset.GetPartition(0)
            n_partitions = self._current_dataset.GetNumberOfPartitions()
            self.state.view_table_multiblock = n_partitions > 1
            self.state.view_table_multiblocks = list(range(n_partitions))
            self.state.view_table_multiblock_active = 0
        else:
            self.state.view_table_multiblock = False
            self.state.view_table_multiblocks = []
            self.state.view_table_multiblock_active = None

    @change("view_table_multiblock_active")
    def update_active_block(self, view_table_multiblock_active, **_):
        if self._current_dataset is None:
            return

        if isinstance(self._current_dataset, dict):
            self._current_block = self._current_dataset.get(
                view_table_multiblock_active, self._current_dataset
            )

        if self._current_dataset.IsA("vtkPartitionedDataSetCollection"):
            self._current_block = self._current_dataset.GetPartitionedDataSet(
                view_table_multiblock_active
            )
        elif self._current_dataset.IsA("vtkPartitionedDataSet"):
            self._current_block = self._current_dataset.GetPartition(
                view_table_multiblock_active
            )
        else:
            self._current_block = self._current_dataset

        if self._current_block.IsA("vtkPartitionedDataSet"):
            self._current_block = self._current_block.GetPartition(0)

        if self._current_block is None:
            self.state.view_table_headers = []
            self.state.view_table_items = []
            return

        pd = self._current_block.GetPointData()
        n_arrays = pd.GetNumberOfArrays()
        array_names = []
        headers = []
        items = None
        for i in range(n_arrays):
            array = pd.GetAbstractArray(i)
            name = array.GetName()
            array_names.append(name)
            headers.append(
                dict(key=name, title=name, sortable=is_sortable(array), align="center")
            )
            if items:
                for entry in items:
                    idx = entry.get("index")
                    value = s(array.GetTuple(idx))
                    entry[name] = value
            else:
                array_size = array.GetNumberOfTuples()
                items = [
                    {"index": i, name: s(array.GetTuple(i))} for i in range(array_size)
                ]
                self.state.view_table_items_length = array_size

        self._current_headers = headers
        self._current_items = items

        self.state.view_table_headers = headers
        self.state.view_table_items = self.sorted_items[
            self._current_page_slice[0] : self._current_page_slice[1]
        ]

    def update_items(self, page, itemsPerPage, sortBy, **_):  # noqa: N803
        self._current_sort_mode = sortBy
        self._current_page_slice = ((page - 1) * itemsPerPage, page * itemsPerPage)
        if len(self._current_items) == 0:
            self.load_data_from_proxy()
        else:
            self.state.view_table_items = self.sorted_items[
                self._current_page_slice[0] : self._current_page_slice[1]
            ]
