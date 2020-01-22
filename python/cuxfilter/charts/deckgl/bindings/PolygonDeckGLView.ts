import {LayoutDOM, LayoutDOMView} from "models/layouts/layout_dom"
import {div} from "core/dom"
import {PolygonDeckGL} from "./PolygonDeckGL"
import {ContentBox} from "core/layout"
// import {LinearColorMapper} from "models/mappers/linear_color_mapper"
 
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
    this.el.style.width = `${this.model.properties.width.spec.value}px`
    this.el.style.height =`${this.model.properties.height.spec.value}px`


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

    console.log(this.model.color_mapper)
    // let col_name: string = this.model.layer_spec['getFillColor'].replace("@@=", '')
    
    // console.log(this.model.color_mapper.rgba_mapper.v_compute(source['prediction']))
    // source['color'] = this.model.color_mapper.rgba_mapper.v_compute(source['prediction'])
    data = parseData(source, this.model.color_mapper)
    // console.log(this.model.color_mapper.v_compute(data[['layer_spec']['getFillColor'].replace("@@==", '')]))
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

function parseData(obj: any, cm: any): Array<any> {
  let b: Array<any> = []
  for (let key in obj) {
      let value = obj[key];
      for (let i in value) {
        if( key == cm.name){
          console.log(value[i])
          console.log(cm.rgba_mapper.v_compute([value[i]]))
          let buf8_0: string = cm.rgba_mapper.v_compute([value[i]])
          b[parseInt(i)]['color'] = [buf8_0[0], buf8_0[1], buf8_0[2], buf8_0[3]]
        }
          if (b.length <= +i) {
              b.push({[key]: value[i]})
          } else {
              b[parseInt(i)][key] = value[i]
          }
      }
 }
 return b

}