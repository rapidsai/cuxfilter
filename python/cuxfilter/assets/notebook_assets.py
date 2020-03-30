import panel as pn

deck = "https://unpkg.com/deck.gl@latest/dist.min.js"
mapbox = "https://api.tiles.mapbox.com/mapbox-gl-js/v1.4.0/mapbox-gl.js"
deck_json = "https://unpkg.com/@deck.gl/json@8.1.0/dist.min.js"


def load_notebook_assets():
    pn.extension()
    pn.extension(
        js_files={"deck": deck, "mapbox": mapbox, "deck_json": deck_json},
        css_files=[
            "https://api.tiles.mapbox.com/mapbox-gl-js/v1.4.0/mapbox-gl.css"
        ],
    )
