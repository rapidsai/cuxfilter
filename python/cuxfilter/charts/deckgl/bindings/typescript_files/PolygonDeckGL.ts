import {PolygonDeckGLView} from "./PolygonDeckGLView"
import {ColumnDataSource} from "models/sources/column_data_source"
import {LayoutDOM} from "models/layouts/layout_dom"
import * as p from "core/properties"
import {LinearColorMapper} from "models/mappers/linear_color_mapper"
import {ColorMapper} from "models/mappers/color_mapper"


const Greys9 = () => ["#000000", "#252525", "#525252", "#737373", "#969696", "#bdbdbd", "#d9d9d9", "#f0f0f0", "#ffffff"]

// We must also create a corresponding JavaScript BokehJS model subclass to
// correspond to the python Bokeh model subclass. In this case, since we want
// an element that can position itself in the DOM according to a Bokeh layout,
// we subclass from ``LayoutDOM``
export namespace PolygonDeckGL {
    export type Props = LayoutDOM.Props & {
        x: p.Property<string>
        layer_spec: p.Property<object>
        deck_spec: p.Property<object>
        data_source: p.Property<ColumnDataSource>
        color_mapper: p.Property<ColorMapper>
        tooltip: p.Property<boolean>
      }
  export type Attrs = p.AttrsOf<Props>
 
}

export interface PolygonDeckGL extends PolygonDeckGL.Attrs {}

export class PolygonDeckGL extends LayoutDOM {
  properties: PolygonDeckGL.Props

  constructor(attrs?: Partial<PolygonDeckGL.Attrs>) {
    super(attrs)
  }

  // The ``__name__`` class attribute should generally match exactly the name
  // of the corresponding Python class. Note that if using TypeScript, this
  // will be automatically filled in during compilation, so except in some
  // special cases, this shouldn't be generally included manually, to avoid
  // typos, which would prohibit serialization/deserialization of this model.
  static __name__ = "PolygonDeckGL"

  static init_PolygonDeckGL() {
    // This is usually boilerplate. In some cases there may not be a view.
    this.prototype.default_view = PolygonDeckGLView

    // The @define block adds corresponding "properties" to the JS model. These
    // should basically line up 1-1 with the Python model class. Most property
    // types have counterparts, e.g. ``bokeh.core.properties.String`` will be
    // ``p.String`` in the JS implementatin. Where the JS type system is not yet
    // as rich, you can use ``p.Any`` as a "wildcard" property type.
    this.define<PolygonDeckGL.Props>({
      x: [p.String],
      layer_spec:   [ p.Any ],
      deck_spec: [ p.Any ],
      data_source: [ p.Instance ],
      color_mapper: [ p.Instance,  () => new LinearColorMapper({palette: Greys9()}) ],
      tooltip: [p.Boolean]
    })
  }
}