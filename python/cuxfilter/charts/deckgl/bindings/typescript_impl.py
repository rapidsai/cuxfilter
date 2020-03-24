TS_CODE = """
import {LayoutDOM, LayoutDOMView} from "models/layouts/layout_dom"
import {div} from "core/dom"
import {ContentBox} from "core/layout"
import {ColumnDataSource} from "models/sources/column_data_source"
import * as p from "core/properties"
import {LinearColorMapper} from "models/mappers/linear_color_mapper"

declare namespace deck {
  class Layer {
    constructor(OPTIONS: object)
  }
  class PolygonLayer extends Layer {}
  class JSONConverter {
    constructor(OPTIONS: object)
    convert(d: object): unknown
  }
  class DeckGL {
      constructor(OPTIONS: object)
      setProps(d: object): void
      pickObject(d: object): unknown
      pickMultipleObjects(d: object): unknown
  }
}

// To create custom model extensions that will render on to the HTML canvas
// or into the DOM, we must create a View subclass for the model.
//

// In this case we will subclass from the existing BokehJS ``LayoutDOMView``
export class PolygonDeckGLView extends LayoutDOMView {

  model: PolygonDeckGL
  private _layer: deck.Layer
  private _deckgl: deck.DeckGL
  private _jsonConverter: deck.JSONConverter
  private _container: HTMLElement
  private _tooltip: HTMLElement
  private _loaded: boolean = false
  private _current_selection: Set<number>

  connect_signals(): void {
    super.connect_signals()
    // Set a listener so that when the Bokeh data source has a change
    // event, we can process the new data
    this.connect(this.model.data_source.streaming, () => {
        this._update_deck()
    })
    this.connect(this.model.data_source.change, () => {
      this._update_deck()
    })

    this.connect(this.model.data_source.patching, () => {
    this._update_deck()
    })

    this.connect(this.model.data_source.selected.change, () => {
      this._update_deck()
    })
    this.connect(this.model.data_source._select, () => {
      this._update_deck()
    })
    this.connect(this.model.data_source.inspect, () => {
      this._update_deck()
    })
  }

  initialize(): void {
    super.initialize()
    this._init()
  }

 private _init(): void {
        this._current_selection = new Set()
        this._container = div({
          style: {
            width:  '100%',
            height: '100%'
          },
          id: 'deck-gl',
        })
        if(this.model.tooltip){
          this._tooltip = div({
            style: {
              position: 'absolute',
              'z-index': 1,
              'point-events': 'none',
              'background-color': 'black',
              'color': 'white',
              'padding': '10px'
            },
            id: 'tooltip',
          })
          this._container.appendChild(this._tooltip)
        }

        // document.body.appendChild(this._container)
        this.el.appendChild(this._container)

        const {JSONConverter} = deck;
        this._jsonConverter = new JSONConverter({
          configuration: {}
        })

        this._create_deck()

 }

 private _create_deck(): void {

      let options: any = {
          data: this.get_data(),
          ...this._jsonConverter.convert(this.model.layer_spec),
          getFillColor: (obj: object) => this._getFillColor(obj),
          onClick: (obj: object) => this._onclickHandler(obj),
      }

      if(this.model.tooltip){
        options['onHover'] = (info: any) => this._setTooltip(info)
      }

      this._layer = new deck.PolygonLayer(options)

      this._deckgl = new deck.DeckGL({
          ...this.model.deck_spec,
          container: this._container,
          layers: [this._layer]
      })

      this._loaded = true

      # console.log("create_deck", this._deckgl)
 }

 private _update_deck(): void {
      if (this._loaded == false){
          this._init()
      }
      //console.log('update deck called')

      let options: any = {
          data: this.get_data(),
          ...this._jsonConverter.convert(this.model.layer_spec),
          getFillColor: (obj: object) => this._getFillColor(obj),
          onClick: (obj: object) => this._onclickHandler(obj),
      }

      if(this.model.tooltip){
        options['onHover'] = (info: any) => this._setTooltip(info)
      }
      this._layer = new deck.PolygonLayer(options)

      this._deckgl.setProps({
          layers: [this._layer]
      })

      //console.log("update_deck", this._deckgl)
 }

  render(): void {
      super.render()
      this._update_deck()
  }

  get_data(): Array<any> {
    let data: Array<any>
    const source: any = this.model.data_source.data
    const x: string = this.model.x
    # console.log(this._current_selection)
    data = parseData(
      x, source, this.model.color_mapper, this._current_selection
    )
    return data
  }

  get child_models(): LayoutDOM[] {
    return []
  }

  _update_layout(): void {
    this.layout = new ContentBox(this.el)
    this.layout.set_sizing(this.box_sizing())

  }

  private _onclickHandler(obj: any): void {
      if(!this._current_selection.has(obj.index)){
        this._current_selection.add(obj.index)
      }else{
        this._current_selection.delete(obj.index)
      }
      this.model.data_source.selected.indices = Array.from(
          this._current_selection.values()
      );
  }

  private _getFillColor(obj: any): void {
    return obj.__color__
  }

  private _setTooltip(info: any): void {
    if (info.object) {
      let content = ''
      for(let key in info.object){
        if(key !== 'coordinates' && key !== '__color__'){
          let val = Math.round(info.object[key]*1000000)/1000000
          content += `<b>${key}</b>: ${val} <br/>`
        }
      }
      this._tooltip.innerHTML = content
      this._tooltip.style.display = 'block'
      this._tooltip.style.left = (info.x+12) + 'px'
      this._tooltip.style.top = (info.y+12) + 'px'
    } else {
      this._tooltip.style.display = 'none'
    }
  }
}

function parseData(
    x: string, obj: any, cm: any, _current_selection: Set<number>
): Array<any> {

  // create a object with x_col values as keys, to later add color properties
  let value_x_column: any =  obj[x]
  let b: Array<any> = []

  for (let value_x in value_x_column) {
    if (b.length <= +value_x) {
        b.push({[x]: value_x_column[value_x]})
    } else {
        b[parseInt(value_x)][x] = value_x_column[value_x]
    }
  }

  for (let key in obj) {
      let value = obj[key];
      for (let i in value) {
        if( key == cm.name && _current_selection.size == 0){

          let buf8_0: string = cm.rgba_mapper.v_compute([value[i]])
          b[parseInt(i)]['__color__'] = [
              buf8_0[0], buf8_0[1], buf8_0[2], buf8_0[3]
          ]

        }else if( key == cm.name && _current_selection.has(+i)){

          let buf8_0: string = cm.rgba_mapper.v_compute([value[i]])
          b[parseInt(i)]['__color__'] = [
              buf8_0[0], buf8_0[1], buf8_0[2], buf8_0[3]
          ]

        }else if( key == cm.name && !_current_selection.has(+i)){

          b[parseInt(i)]['__color__'] = [211, 211, 211, 50]

        }
        if (key !== x) {
          if (b.length <= +i) {
              b.push({[key]: value[i]})
          } else {
              b[parseInt(i)][key] = value[i]
          }
        }
      }
 }

  return b

}



const Greys9 = () => [
    "#000000", "#252525", "#525252", "#737373", "#969696",
    "#bdbdbd", "#d9d9d9", "#f0f0f0", "#ffffff"
]

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
        color_mapper: p.Property<LinearColorMapper>
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
    // ``p.String`` in the JS implementatin. Where the JS type system is not
    // yet as rich, you can use ``p.Any`` as a "wildcard" property type.

    this.define<PolygonDeckGL.Props>({
      x: [p.String],
      layer_spec:   [ p.Any ],
      deck_spec: [ p.Any ],
      data_source: [ p.Instance ],
      color_mapper: [ p.Instance,  () => new LinearColorMapper(
          {palette: Greys9()}
      ) ],
      tooltip: [p.Boolean]
    })
  }
}

"""
