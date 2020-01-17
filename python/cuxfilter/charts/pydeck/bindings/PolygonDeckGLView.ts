import {LayoutDOM, LayoutDOMView} from "models/layouts/layout_dom"
import {div} from "core/dom"
import {PolygonDeckGL} from "./PolygonDeckGL"
import {ContentBox} from "core/layout"

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
    this.connect(this.model.data_source.streaming, () => {
       console.log('updated data....')
       this._update_deck()
    })
    this.connect(this.model.data_source.change, () => {
      console.log('updated data....')
      this._update_deck()
    })

   this.connect(this.model.data_source.patching, () => {
    console.log('updated data....')
    this._update_deck()
    })

    this.connect(this.model.data_source.selected.change, () => {
      console.log('updated data....')
      this._update_deck()
   })
   this.connect(this.model.data_source._select, () => {
    console.log('updated data....')
    this._update_deck()
 })
    this.connect(this.model.data_source.inspect, () => {
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
    this.el.style.margin = '0'
    this.el.style.padding = '0'
    this.el.style.overflow = 'hidden'
    


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
            width: this.model.properties.width.spec.value+"px",
            height: this.model.properties.height.spec.value+"px",
          },
          id: 'deck-gl',
          class: 'bk-clearfix'
        })
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
    this.layout = new ContentBox(this.el)
    this.layout.set_sizing(this.box_sizing())

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