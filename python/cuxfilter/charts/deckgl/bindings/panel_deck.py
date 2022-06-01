import panel as pn
import param

css = """
.multi-select{
    color: white;
    z-index: 100;
    background: rgba(44,43,43,0.5);
    border-radius: 1px;
    width: 120px !important;
    height: 30px !important;
}
.multi-select > .bk {
    padding: 5px;
    width: 120px !important;
    height: 30px !important;
}

.deck-chart {
    z-index: 10;
    position: initial !important;
}
"""

pn.config.raw_css += [css]


class PanelDeck(param.Parameterized):
    """
    PanelDeck class for panel.pane.DeckGL + multi_select(Boolean) parameter
    """

    x = param.String("x")
    data = param.DataFrame()
    colors = param.DataFrame()
    indices = set()
    multi_select = param.Boolean(False, doc="multi-select")
    callback = param.Callable()
    spec = param.Dict()
    default_color = param.List([211, 211, 211, 50])
    sizing_mode = param.String("stretch_both")
    height = param.Integer(400)
    width = param.Integer(400)
    tooltip_include_cols = param.List(
        [], doc="list of columns to include in tooltip"
    )

    @property
    def valid_indices(self):
        return self.indices.intersection(self.data.index)

    def get_tooltip_html(self):
        """
        get tooltip info from dataframe columns, if not already present
        """
        html_str = ""
        tooltip_columns = (
            self.data.columns
            if len(self.tooltip_include_cols) == 0
            else self.tooltip_include_cols
        )

        for i in tooltip_columns:
            html_str += f"<b> {i} </b>: {{{i}}} <br>"
        return {"html": html_str}

    def __init__(self, **params):
        """
        initialize deck html object, and set a listener on self.data
        """
        super(PanelDeck, self).__init__(**params)
        self.spec["layers"][0]["data"] = self.data
        self.pane = pn.pane.DeckGL(
            self.spec,
            sizing_mode=self.sizing_mode,
            height=self.height,
            tooltips={self.spec["layers"][0]["id"]: self.get_tooltip_html()},
            css_classes=["deck-chart"],
        )
        self.param.watch(self._update, ["data"])

    def selected_points(self):
        """
        returns a list of currently selected column_x values as a list
        """
        return self.data[self.x].loc[self.valid_indices].tolist()

    @pn.depends("pane.click_state")
    def click_event(self):
        """
        callback for click events, highlights the selected indices
        (single_select/multi_select) and sets the color of
        unselected indices to default_color
        """
        index = self.pane.click_state.get("index", -1)
        old_indices = self.valid_indices
        if index == -1:
            index = slice(0, 0)
            self.indices.clear()
            self.data[self.colors.columns] = self.colors
        else:
            if self.multi_select:
                if index not in self.indices:
                    self.indices.add(index)
                else:
                    self.indices.remove(index)
            else:
                if index in self.indices:
                    self.indices.clear()
                else:
                    self.indices.clear()
                    self.indices.add(index)
            temp_colors = self.colors.copy()
            if len(self.indices) > 0:
                temp_colors.loc[
                    set(self.data.index) - self.indices, self.colors.columns
                ] = self.default_color
            self.data[self.colors.columns] = temp_colors
        self._update_layer_data(self.data)
        self.callback(
            self.data[self.x].loc[old_indices].tolist(),
            self.data[self.x].loc[self.valid_indices].tolist(),
        )

    def _update_layer_data(self, data):
        self.pane.object["layers"][0]["data"] = data
        self.pane.param.trigger("object")

    def _update(self, event):
        """
        trigger deck_gl pane when layer data is updated
        """
        if event.name == "data":
            self._update_layer_data(self.data)

    def view(self):
        """
        view object
        """
        x = pn.Column(
            self.param.multi_select,
            sizing_mode=self.sizing_mode,
            css_classes=["multi-select"],
        )

        return pn.Column(
            x,
            self.click_event,
            self.pane,
            width=self.width,
            height=self.height,
            sizing_mode=self.sizing_mode,
        )
