import panel as pn
import param
import pydeck as pdk

raw_css = '''
.multi-select {
color: white;
z-index: 100;
background-color: #2c2b2b;
border-radius: 1px;
width: 100px !important;
height: 30px;
}

.deck-chart {
    z-index: 10;
    position: initial !important;
}
'''

pn.extension('deckgl', raw_css=[raw_css])


class panel_deck(param.Parameterized):
    x = param.String("x")
    data = param.DataFrame()
    colors = param.DataFrame()
    indices = set()
    multi_select = param.Boolean(False, doc='multi-select')
    callback = param.Callable()
    spec = param.Dict()
    default_color = param.List([211, 211, 211, 50])
    sizing_mode = param.String("scale_both")
    height = param.Integer(400)
    width = param.Integer(400)

    def get_tooltip_html(self):
        html_str = ''
        tooltip_columns = list(
            set(self.data.columns) - set(
                ['index', 'coordinates'] + list(self.colors.columns)
                )
        )
        for i in tooltip_columns:
            html_str += '<b> %s </b>: {%s} <br><br>' % (i, i)
        return html_str

    def __init__(self, **params):
        super(panel_deck, self).__init__(**params)
        self._view_state = pdk.ViewState(
            **self.spec['initialViewState'],
            bearing=0.45,
        )
        self._layers = pdk.Layer(
            'PolygonLayer',
            data=self.data,
            **self.spec['layers'][0]
        )
        self._tooltip = {"html": self.get_tooltip_html()}

        self._deck = pdk.Deck(
            mapbox_key=self.spec['mapboxApiAccessToken'],
            layers=[self._layers],
            initial_view_state=self._view_state,
            tooltip=self._tooltip
        )
        self.pane = pn.pane.DeckGL(
            self._deck, sizing_mode=self.sizing_mode, height=self.height,
            width=self.width, css_classes=['deck-chart']
        )
        self.param.watch(self._update, ['data'])

    @pn.depends('pane.click_state')
    def click_event(self):
        index = self.pane.click_state.get('index', -1)
        old_indices = list(self.indices)
        if index == -1:
            index = slice(0, 0)
            self.indices = set()
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
        self._layers.data = self.data
        self.pane.param.trigger('object')
        self.callback(
            self.data[self.x].loc[old_indices].tolist(),
            self.data[self.x].loc[list(self.indices)].tolist()
        )

    def _update(self, event):
        if event.name == 'data':
            self._layers.data = self.data
        self.pane.param.trigger('object')

    def view(self):
        x = pn.Column(self.param.multi_select, css_classes=['multi-select'])

        return pn.Column(
            self.click_event, x, self.pane,
            width=self.width, height=self.height, sizing_mode='scale_both'
        )
