import {LayoutDOM, LayoutDOMView} from "models/layouts/layout_dom"
import {ColumnDataSource} from "models/sources/column_data_source"
import * as p from "core/properties"
import {div} from "core/dom"


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

  connect_signals(): void {
    super.connect_signals()
    // Set a listener so that when the Bokeh data source has a change
    // event, we can process the new data
    this.connect(this.model.data_source.change, () => {
       console.log('updated data....')
       this._update_deck()
    })

  }

  initialize(): void {
    super.initialize()
    // this.el.style.margin = '0';
    // this.el.style.overflow = 'hidden';
    // this.el.style.width = this.model.properties.width.spec.value+'px'
    // this.el.style.height= this.model.properties.height.spec.value+'px'
    this.el.style.position = 'relative';
    this.el.style.height = this.model.properties.height.spec.value+'px'
    this.el.style.height = this.model.properties.height.spec.value+'px'
    


    const url = "https://unpkg.com/deck.gl@latest/dist.min.js"
    const script = document.createElement("script")
    script.onload = () => this._load_script2()
    script.async = false
    script.src = url
    document.head.appendChild(script)    
  }

  private _load_script2(): void {
    const url = "https://api.tiles.mapbox.com/mapbox-gl-js/v1.4.0/mapbox-gl.js"
    const script = document.createElement("script")
    script.onload = () => this._load_script3()
    script.async = false
    script.src = url
    document.head.appendChild(script)
  }

  private _load_script3(): void {
    const url = "https://unpkg.com/@deck.gl/json@latest/dist.min.js"
    const script = document.createElement("script")
    script.onload = () => this._init()
    script.async = false
    script.src = url
    document.head.appendChild(script)
  }
  
 private _init(): void {

        this._container = div({
          style: {
            width: '100%',
            height: '100%',
            margin: 0,
            overflow: 'hidden'
          },
          id: 'deck-gl',
          class: 'bk-clearfix'
        })
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
          onClick: (obj: object) => this._onclickHandler(obj)
      }

      this._layer = new deck.PolygonLayer(options)

      this._deckgl = new deck.DeckGL({
          ...this.model.deck_spec,
          container: this._container,
          layers: [this._layer]
      })      
 }

 private _update_deck(): void {

      console.log('update deck called')

      let options: any = {
          data: this.get_data(),
          ...this._jsonConverter.convert(this.model.layer_spec),
          onClick: (obj: object) => this._onclickHandler(obj)
      }
      this._layer = new deck.PolygonLayer(options)

      this._deckgl.setProps({
          layers: [this._layer]
      })
 }

  render(): void {
      super.render()
      this._update_deck()   
  }

  get_data(): Array<any> {
    let data: Array<any>
    const source: any = this.model.data_source.data
    data = parseData(source)
    console.log(data)
    return data
  }

  get child_models(): LayoutDOM[] {
    return []
  }

  _update_layout(): void {
    
  }
    
  private _onclickHandler(obj: any): void {
      console.log(obj)
      this.model.data_source.selected.multiline_indices = obj.object
  }
}

function parseData(obj: any): Array<any> {
  let b: Array<any> = []
  for (let key in obj) {
      let value = obj[key];
      for (let i in value) {
          if (b.length <= +i) {
              b.push({[key]: value[i]})
          } else {
              b[parseInt(i)][key] = value[i]
          }
      }
 }
 return b

}
  

// We must also create a corresponding JavaScript BokehJS model subclass to
// correspond to the python Bokeh model subclass. In this case, since we want
// an element that can position itself in the DOM according to a Bokeh layout,
// we subclass from ``LayoutDOM``
export namespace PolygonDeckGL {
    export type Props = LayoutDOM.Props & {
        layer_spec: p.Property<object>
        deck_spec: p.Property<object>
        data_source: p.Property<ColumnDataSource>
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
      layer_spec:   [ p.Any ],
      deck_spec: [ p.Any ],
      data_source: [ p.Instance ]
    })
  }
}