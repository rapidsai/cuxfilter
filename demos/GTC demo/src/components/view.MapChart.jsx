import React, { Component } from "react";
import {render} from "react-dom";


// https://deck.gl/#/
import DeckGL, {ScatterplotLayer, GeoJsonLayer} from 'deck.gl';
import {StaticMap} from 'react-map-gl';
import './scss/mapbox-gl';

import BarChart from './component.BarChart'

// https://github.com/dmitrymorozoff/react-circle-slider
import { CircleSlider } from "react-circle-slider";


// EXTERNAL
// RAPIDS cuXFilter
// NOTE: if cuXfilter-client.js is updated, MUST rebuild GTC demo from source
import cuXfilter from "../../../../client_side/dist/cuXfilter-client.js"


// scss
import './scss/mapchart-style';

// location of zip3 geoJson
const geoURL ='./data/zip3-ms-rhs-lessprops.json';

// list of bank names in dataset for filtering
import bankList from '../data/banklist-id.json';


class MapChart extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			// configURL: '/config.json', // EXTERNAL
			xFilter: undefined,
			engine: 'cudf',
			ip: undefined,
			dataset: undefined,
			memformat: 'arrow',
			sessions: true,
			mapboxtoken: undefined, // NOTE: Map underlay requires MapBox Token set in config.json - https://www.mapbox.com/help/define-access-token/
			geoData: undefined,
			hover: undefined,
			currentZip: undefined,
			totalDP: 0,
			currentDP: 0,
			mapOpacity: 100,
			mapScale: 10,
			colorRange5: [[49,130,189, 100], [107,174,214, 100], [123, 142, 216, 100], [226,103,152, 100], [255,0,104, 100], [50,50,50, 100]], // Note: make sure matches css and opacity update
			bankList: bankList.banks,
			selectedBank: "All",
			chart1Bins: 10,
			chart2Bins: 10,
			chart3Bins: 10,
			chart1Data: [],
			chart2Data: [],
			chart3Data: [],
			chart1Domain: undefined,
			chart2Domain: undefined,
			chart3Domain: undefined,
			active: true,
			error: false
		}

		// event binding
		// https://reactjs.org/docs/handling-events.html

		this.areaHover = this.areaHover.bind(this)
		this.mapOpacitySelection = this.mapOpacitySelection.bind(this)
		this.mapScaleSelection = this.mapScaleSelection.bind(this)

		this.filterZip3 = this.filterZip3.bind(this)

		this.bankSelection = this.bankSelection.bind(this)

		this.chart1BinSelection = this.chart1BinSelection.bind(this)
		this.chart2BinSelection = this.chart2BinSelection.bind(this)
		this.chart3BinSelection = this.chart3BinSelection.bind(this)

		// super nested this blah...
		this.chart1BinUpdate = this.debounce(this.chart1BinUpdate.bind(this), 100)
		this.chart2BinUpdate = this.debounce(this.chart2BinUpdate.bind(this), 100)
		this.chart3BinUpdate = this.debounce(this.chart3BinUpdate.bind(this), 100)

		this.filterCharts = this.filterCharts.bind(this)
		this.resetChartFilter = this.debounce(this.resetChartFilter.bind(this), 100)


		this.updateSize = this.updateSize.bind(this)
		this.updateComplete = this.updateComplete.bind(this)

		this.resetAllFilters = this.resetAllFilters.bind(this)
		this.resetInit = this.resetInit.bind(this)
		this.switchMode = this.switchMode.bind(this)

	}

	// Limit calls
	// https://codeburst.io/throttling-and-debouncing-in-javascript-b01cad5c8edf
	// https://stackoverflow.com/questions/23123138/perform-debounce-in-react-js
	debounce (func, delay){
	  console.log("debounce init")
	  let inDebounce
	  return function() {
	    const context = this
	    const args = arguments
	    clearTimeout(inDebounce)
	    inDebounce = setTimeout(() => func.apply(context, args), delay)
	  }
	}


	componentDidMount() {
		// so nav click always moves to top of page
		window.scrollTo(0, 0);


		// cuXfilter emits an event when data is updated
		// add data update event listener
		window.addEventListener('updateGroupEvent', (e) => {console.log("Triggered updateGroupEvent: ", e.detail.column); this.parseMapData(e)} )

		// add data update event listener
		window.addEventListener('updateHistEvent', (e) => {console.log("Triggered updateHistEvent: ", e.detail.column); this.parseChartData(e)} )

		// add updated filtered data size listener
 		window.addEventListener('updateSizeEvent', (e) => {console.log("Triggered updateSizeEvent"); this.updateSize()} )

 		// add all updates completed listener
		window.addEventListener('allUpdatesComplete', (e) => { this.updateComplete()} )


		// START
		// Start init loading chain (loadConfig -> initCuXFilter -> loadGeoJson -> setMapChartDimensions)
		this.loadConfig().then(() => {
			this.initCuXFilter();
		}).catch((err) => {
			console.log(err);
		});
	}

	componentWillUnmount(){
		console.log("Unmounting...")

		if(this.state.xFilter != undefined){
			this.state.xFilter.resetAllFilters();
			// end xFilter
			this.state.xFilter.endSession().then((status) => {
				console.log("Umount:", status)
			}).catch((err) => {
				console.log("xFilter endSession error:", err)
			});
		}

	}

	// load external configuration file containing dataset name and cuXfilter ip
	loadConfig(){
		return new Promise((resolve, reject) => {
			console.log('env variable 1',process.env.REACT_APP_demo_mapbox_token);
			console.log('env variable 2', process.env.REACT_APP_server_ip);
			if(process.env.REACT_APP_server_ip === '' || process.env.REACT_APP_demo_dataset_name  === ''){

				this.setState({
					error: true
				})

				reject('config.env error. Make sure the environment variables are set correctly');
			} else{
						if(process.env.REACT_APP_demo_mapbox_token === ''){
							console.log('WARNING: no mapbox token token configured, there will be NO map base layer!')
						}
						console.log("config env loaded successfully");
						// set state
						this.setState({
							ip: process.env.REACT_APP_server_ip, //+ cuXfilter_port,
							dataset: process.env.REACT_APP_demo_dataset_name,
							mapboxtoken: process.env.REACT_APP_demo_mapbox_token
						})
					resolve();
			}
		})


		// fetch(this.state.configURL).then((response) => {
		//   if(response.ok) {
		//     return response.json();
		//   }
		//   throw new Error('Network response was not ok.');
		// }).then((json) => {
		//
		// 	console.log("xFilter Config data loaded.", json)
		//
		// 	// NOTE: check if config.json is filled out correctly
		// 	if(json.server_ip === '' || json.dataset  === '' || json.cuXfilter_port === ''){
		//
		// 		this.setState({
		// 			error: true
		// 		})
		//
		// 		console.log('config.json error. Make sure the config file is fill out correctly');
		// 	} else{
		//
		//
		// 		if(json.demo_mapbox_token === ''){
		// 			console.log('WARNING: no mapbox token token configured, there will be NO map base layer!')
		// 		}
		//
		// 		// set state
		// 		this.setState({
		// 			ip: json.server_ip + ':' + json.cuXfilter_port,
		// 			dataset: json.demo_dataset_name,
		// 			mapboxtoken: json.demo_mapbox_token
		//
		// 		})
		//
		// 		// kick off initialization
		// 		this.initCuXFilter();
		// 	}

		// }).catch((err) => {
		//
		// 	this.setState({
		// 		error: true
		// 	})
		//
		// 	console.log('config.json fetch error. Make sure the config file is setup correctly: ', err);
		// });
	}

	// switch mode between CPU / GPU
	switchMode(){
		if(this.state.engine === 'cudf'){
			this.setState({
				engine: 'pandas'
			})
		} else {
			this.setState({
				engine: 'cudf'
			})
		}

		this.resetInit();


	}

	// end session and reinitialize
	resetInit(){

		this.setState({
			currentZip: undefined,
			totalDP: 0,
			currentDP: 0,
			selectedBank: "All",
			chart1Data: [],
			chart2Data: [],
			chart3Data: [],
			chart1Domain: undefined,
			chart2Domain: undefined,
			chart3Domain: undefined,
			active: true,
			error: false
		})

		// reset
		this.state.xFilter.resetAllFilters()

		// end xFilter
		this.state.xFilter.endSession().then((status) => {
			console.log("reset Init:", status)
			this.initCuXFilter();

		}).catch((err) => {

			this.setState({
				error: true
			})

			console.log("xFilter rest endSession error:", err)
		});

	}

	// setup cuXFilter w/ passed parameters: dataset name (string), cuXfilter ip (often localhost), engine ('cudf' / 'pandas') , use sessions ( true / false ), load type ('ipc' / 'arrow')
	// loads data frame into back end GPU memory
	initCuXFilter(){

		const xFilter = new cuXfilter(this.state.dataset, this.state.ip, this.state.engine, this.state.sessions, this.state.memformat)
		console.log("initializing xFilter to: ", xFilter)

		// initializing
		xFilter.init().then((status) => {
			console.log("xFilter initialized: ", status);

			this.setState({
				xFilter: xFilter,
				active: true
			})

			// Only after initialization is complete should geoJson Load
			this.loadGeoJson();

		}).catch((err) => {

			this.setState({
				error: true
			})

			console.log("xFilter Error: ", err)
		})
	}

	// Load USA zip3 geoJSON boundaries from file
	loadGeoJson(){

		fetch(geoURL).then((response) => {
		  if(response.ok) {
		    return response.json();
		  }
		  throw new Error('Network response was not ok.');
		}).then((json) => {

			console.log("GeoJSON data loaded.", json)
			this.setState({
				geoData: json
			})

			// dependent on geoJson and cuXfilter before able to set dimensions
			this.setMapChartDimensions()

		}).catch((err) => {

			this.setState({
				error: true
			})

		  console.log('Fetch operation error: ', err);
		});
	}

	// initialize dimensions for cross filtering
	setMapChartDimensions(){

		this.setState({
			active: true
		})

		// get table column headings
		const cols = this.state.xFilter.schema;
		console.log("setting dimensions:", cols)

		// initialized dimension variables
		//0: "zip", 1: "dti", 2: "current_actual_upb", 3: "borrower_credit_score", 4: "loan_id", 5: "delinquency_12_prediction", 6: "seller_name"
		this.zip3DIM = this.state.xFilter.dimension(cols[0])
		this.delDIM = this.state.xFilter.dimension(cols[5])
		this.creditDIM = this.state.xFilter.dimension(cols[3])
		this.dtiDIM = this.state.xFilter.dimension(cols[1])
		this.orgDIM = this.state.xFilter.dimension(cols[6])

		// once all dimensions are initialized
		Promise.all([this.zip3DIM.loadDimension(), this.delDIM.loadDimension(), this.creditDIM.loadDimension(), this.dtiDIM.loadDimension(), this.orgDIM.loadDimension()]).then((status) =>{
			console.log("Dims loaded", status)
			const params = {
							'delinquency_12_prediction': ['mean'],
							'current_actual_upb': ['sum']
							}

			// initialize groupBy w/ above parameters to zip3 dimension
			this.zip3GROUP = this.zip3DIM.group(params)

			return(Promise.all([this.zip3GROUP.loadGroup()]))

		}).then((status) => {
			console.log("Groups loaded", status)

			// initial data calculation, triggers update event
			this.zip3GROUP.all()
			this.delDIM.getHist(this.state.chart1Bins)
			this.dtiDIM.getHist(this.state.chart2Bins)
			this.creditDIM.getHist(this.state.chart3Bins)

			// make sure all filters are reset on load in case previously not cleared ( browser tab closed etc )
			this.state.xFilter.resetAllFilters()

		}).catch((err) =>{

			this.setState({
				error: true
			})

			console.log("zip3 dim error ", err)
		})

	}

	// set active status to false from event
	updateComplete(){
		this.setState({
			active: false
		})
	}

	// updates the filtered size from event
	updateSize(){
		if(this.state.xFilter != undefined){

			// assumes first size event its full dataset size
			if(this.state.totalDP === 0){
				this.setState({
					currentDP: this.state.xFilter.size,
					totalDP: this.state.xFilter.size
				})
			} else {
				this.setState({
					currentDP: this.state.xFilter.size // update filtered data frame size
				})
			}

		}
	}


	// parse data to match with Deck.gl required format and merge with zip3 geoJson data
	parseMapData(event){

		const data = this.zip3GROUP.value;
		console.log("parsing to map data: ", data)

		let geoDataFeatures = this.state.geoData.features

		// merge with geoJson counts
		if(geoDataFeatures.length != undefined){

			for(let i=0; i < geoDataFeatures.length; i++){

				// get geoJson ZIP3 value, find match in groupBy data, get index to get data values
				// NOTE: possible optimization here?
				let zip3 = parseFloat(geoDataFeatures[i].properties.ZIP3)
				let index = data.zip.indexOf(zip3)
				if(index > -1){
					geoDataFeatures[i].properties.sum_upb = data.sum_current_actual_upb[index]
					geoDataFeatures[i].properties.delinquency = data.mean_delinquency_12_prediction[index]

				} else {
					// required for filtered of incomplete data
					console.log(zip3 + " not found in geoJSON")
					geoDataFeatures[i].properties.sum_upb = undefined
					geoDataFeatures[i].properties.delinquency = undefined
				}
			}

			this.setState({
				geoData: { type: "FeatureCollection", features: geoDataFeatures }, // new obj required since react only does shallow compare for state change
				error: false
			})

		} else {
			this.setState({
				error: true
			})
		}

	}

	// parse data to match victory charts format
	parseChartData(event){
		console.log("Parsing data for chart...")

		if(event.detail.column === 'delinquency_12_prediction'){

			// calc data for histogram
			if(this.delDIM === undefined){

				this.setState({
					error: true
				})

			} else {

				const chartData = this.formatData(this.delDIM.histogram)

				if(this.state.chart1Domain != undefined){

					this.setState({
						chart1Data: chartData
					})

				} else {

					const max = Math.max(...this.delDIM.histogram.X)
					const min = Math.min(...this.delDIM.histogram.X)

					this.setState({
						chart1Data: chartData,
						chart1Domain: {min:min, max:max}
					})

				}

			}

		}

		if(event.detail.column === 'dti'){

			// calc data for histogram
			if(this.dtiDIM === undefined){

				this.setState({
					error: true
				})

			} else {
				const chartData = this.formatData(this.dtiDIM.histogram)

				if(this.state.chart2Domain != undefined){

					this.setState({
						chart2Data: chartData
					})

				} else {

					const max = Math.max(...this.dtiDIM.histogram.X)
					const min = Math.min(...this.dtiDIM.histogram.X)

					this.setState({
						chart2Data: chartData,
						chart2Domain: {min:min, max:max}
					})

				}
			}
		}

		if(event.detail.column === 'borrower_credit_score'){

			// calc data for histogram
			if(this.creditDIM === undefined){

				this.setState({
					error: true
				})

			} else {
				const chartData = this.formatData(this.creditDIM.histogram)

				if(this.state.chart3Domain != undefined){

					this.setState({
						chart3Data: chartData
					})

				} else {

					const max = Math.max(...this.creditDIM.histogram.X)
					const min = Math.min(...this.creditDIM.histogram.X)

					this.setState({
						chart3Data: chartData,
						chart3Domain: {min:min, max:max}
					})

				}

			}

		}

	}

	// reformat to match victory charts format
	formatData(data){

		let chartData = []

		for(let i=0; i < data.X.length; i++){
			let item = {x: data.X[i], y: data.Y[i]}
			chartData.push(item)
		}

		this.setState({
			error: false
		})

		return (chartData)

	}


	// return map color for zip3 to match color range defined in state
	// NOTE: should match CSS colors of legend
	calcZip3BinColors(d){

		const value = d.properties.delinquency;

		if(this.state.currentZip != undefined && this.state.currentZip != d.properties.ZIP3){
			return([255,255,255, 50])
		}

		if(value == undefined){
			return(this.state.colorRange5[5])

		} else if(value <= 0.196){
			return(this.state.colorRange5[0])

		} else if(value > 0.196 && value <= 0.198) {
			return(this.state.colorRange5[1])

		} else if(value > 0.198 && value <= 0.200) {
			return(this.state.colorRange5[2])

		} else if(value > 0.200 && value <= 0.202) {
			return(this.state.colorRange5[3])

		} else if(value > 0.202) {
			// red alert
			return(this.state.colorRange5[4])

		} else {
			return(this.state.colorRange5[5])
		}
	}

	// scale zip3 bar height
	getElevation(d){

		const value = d.properties.sum_upb;

		if(value != undefined){
			return(value / 100000)
		} else {
			return(100)
		}
	}


	// call cuXfilter for selected zip3
	filterZip3(object){
		const zip = object.object.properties.ZIP3
		console.log("filtering", zip)

		// reset if clicked on again
		if(zip === this.state.currentZip){

			this.setState({
				active: true,
				currentZip: undefined
			})

			this.zip3DIM.resetFilters()

		} else {

			this.setState({
				active: true,
				currentZip: zip
			})

			this.zip3DIM.resetThenFilter(parseFloat(zip))

		}

	}

	// call cuXFilter for bank name
	// NOTE: bank name must exactly match that in dataset
	filterBanks(value){
		console.log("Filtering Bank:", value)

		this.setState({
			active: true,
			currentZip: undefined
		})

		if(value === 'All'){
			this.orgDIM.resetFilters()
		} else {
			this.orgDIM.resetThenFilter(parseFloat(value))
		}

	}

	// chart selected filter or reset
	filterCharts(selectedDomain, name){

		if(name == "chart1"){

			// manually check if full domain is selected reset filter
			if(selectedDomain.min <= this.state.chart1Domain.min && selectedDomain.max >= this.state.chart1Domain.max){

				console.log("resetting chart1...")
				this.delDIM.resetFilters()

			} else {
				//range error checking
				const min = Math.max(selectedDomain.min, this.state.chart1Domain.min)
				const max = Math.min(selectedDomain.max, this.state.chart1Domain.max)

				console.log("Filtering: ", name, min, max)

				// filter
				this.delDIM.resetThenFilter([min, max])
			}

			this.setState({
				active: true
			})

		}


		if(name == "chart2"){

			// manually check if full domain is selected reset filter
			if(selectedDomain.min <= this.state.chart2Domain.min && selectedDomain.max >= this.state.chart2Domain.max){

				console.log("resetting chart2...")
				this.dtiDIM.resetFilters()

			} else {
				//range error checking
				const min = Math.max(selectedDomain.min, this.state.chart2Domain.min)
				const max = Math.min(selectedDomain.max, this.state.chart2Domain.max)

				console.log("Filtering: ", name, min, max)

				// filter
				this.dtiDIM.resetThenFilter([min, max])
			}

			this.setState({
				active: true
			})

		}

		if(name == "chart3"){

			// manually check if full domain is selected reset filter
			if(selectedDomain.min <= this.state.chart3Domain.min && selectedDomain.max >= this.state.chart3Domain.max){

				console.log("resetting chart3...")
				this.creditDIM.resetFilters()

			} else {

				//range error checking
				const min = Math.max(selectedDomain.min, this.state.chart3Domain.min)
				const max = Math.min(selectedDomain.max, this.state.chart3Domain.max)

				console.log("Filtering: ", name, min, max)

				// filter
				this.creditDIM.resetThenFilter([min, max])
			}

			this.setState({
				active: true
			})

		}

	}

	// reset single chart filter
	resetChartFilter(name){

		if(name == "chart1"){
			console.log("resetting chart1...")
			this.delDIM.resetFilters()

			this.setState({
				active: true,
				chart1Domain: undefined
			})

		}

		if(name == "chart2"){
			console.log("resetting chart2...")
			this.dtiDIM.resetFilters()

			this.setState({
				active: true,
				chart2Domain: undefined
			})

		}

		if(name == "chart3"){
			console.log("resetting chart3...")
			this.creditDIM.resetFilters()

			this.setState({
				active: true,
				chart3Domain: undefined
			})

		}
	}

	// reset all cuXfilters
	resetAllFilters(){

		console.log("clearing all filters...")

		// Note: still bug that filter domain hilight wont reset

		this.setState({
			active: true,
			currentZip: undefined,
			selectedBank: 'All'
		})

		this.state.xFilter.resetAllFilters()

	}

	// chart bin size on change
	chart1BinSelection(value){
		this.setState({
			chart1Bins: value
		})
		this.chart1BinUpdate()
	}

	// chart bin size cuXfilter histogram update
	// NOTE: update should be debounced
	chart1BinUpdate(){

		this.delDIM.getHist(this.state.chart1Bins)
	}

	// chart bin size on change
	chart2BinSelection(value){
		this.setState({
			chart2Bins: value
		})
		this.chart2BinUpdate()
	}

	// chart bin size cuXfilter histogram update
	// NOTE: update should be debounced
	chart2BinUpdate(){

		this.dtiDIM.getHist(this.state.chart2Bins)
	}

	// chart bin size on change
	chart3BinSelection(value){
		this.setState({
			chart3Bins: value
		})
		this.chart3BinUpdate()
	}

	// chart bin size cuXfilter histogram update
	// NOTE: update should be debounced
	chart3BinUpdate(){

		this.creditDIM.getHist(this.state.chart3Bins)
	}

	// update map opacity
	mapOpacitySelection(opacity){
		this.setState({
			colorRange5: [[49,130,189, opacity], [107,174,214, opacity], [123, 142, 216, opacity], [226,103,152, opacity], [255,0,104, opacity], [50,50,50, opacity]], // NOTE: make sure to match range in state var
			mapOpacity: opacity
		})
	}

	// update map bar height
	mapScaleSelection(value){

		this.setState({
			mapScale: value
		})
	}

	// bank name on change
	bankSelection(event){
		this.setState({
			selectedBank: event.target.value
		})
		// to avoid state race condition
		this.filterBanks(event.target.value);
	}

	// create bank names from JSON file
	buildBankList(){
		const list = this.state.bankList.map((d,i) => {
			return(<option value={i} key={i}>{d}</option>)
		})

		return(<select className="mapchart-bank-list" value={this.state.selectedBank} onChange={this.bankSelection}>
				<option value="All">All Banks</option>
				{list}
			   </select>)
	}

	// get area details on zip3 hover
	areaHover(object){
		if(object != undefined && object.object != undefined && object.object.properties != undefined){
			this.setState({
				hover: object.object.properties
			})
		} else {
			this.setState({
				hover: undefined
			})
		}

	}

	// update area details on zip3 hover
	buildAreaHover(){

		if(this.state.hover != undefined){
			let zip3 = 0
			let score = 0
			let upb = 0

			if(this.state.hover.ZIP3 != undefined){
				zip3 = this.state.hover.ZIP3
			}

			if(this.state.hover.delinquency != undefined){
				score = this.state.hover.delinquency.toFixed(3)
			}

			if(this.state.hover.sum_upb != undefined){
				upb = this.state.hover.sum_upb.toLocaleString()
			}

			return(<div className={"mapchar-selected-area"}>3zip: {zip3}xx <br/> score: {score} <br/> upb: {upb} </div>)

		} else {
			return(<div className={"mapchart-selected-area"}>none</div>)
		}

	}

	// update status bar
	buildHeaderStatus(){

		let style = {}
		let classVar = 'mapchart-total-bar-' + this.state.engine;
		if(this.state.error){
			style.width = 100 + '%'
			style.backgroundColor = 'orange'
		} else if(this.state.active){
			classVar = classVar + ' stripes';
		} else if(this.state.totalDP > 0){
			style.marginRight = 100 - ((this.state.currentDP / this.state.totalDP) * 100 ) + '%'
			style.width = (this.state.currentDP / this.state.totalDP) * 100 + '%'
		} else {
			style.width = 100 + '%'
			style.backgroundColor = 'orange'
		}

		return(<div className={classVar} style={style}></div>)
	}


	// build map with or without mapbox
	buildMap(){

	// Initial map viewport settings
	const initialViewState = {
		  longitude: -101,
		  latitude: 37,
		  zoom: 3,
		  pitch: 0,
		  bearing: 0
		}

	// deck.gl configuration
	 const geoLayer = new GeoJsonLayer({
			id: 'geojson-layer',
			data: this.state.geoData,
			visible: true,
			highlightColor: [200,200,200, 200],
			autoHighlight: true,
			wireframe: false,
			pickable: true,
			stroked: false, // only on extrude false
			filled: true,
			extruded: true,
			elevationScale: this.state.mapScale / 100,
			lineWidthScale: 10, // only if extrude false
			lineWidthMinPixels: 1,
			getFillColor: (d) => { return( this.calcZip3BinColors(d) ) },
			getLineColor: [0, 188, 212, 100],
			getRadius: 100, // only if points
			getLineWidth: 10,
			getElevation: (d) => { return( this.getElevation(d) ) },
			updateTriggers: { getFillColor: [this.state.mapOpacity, this.state.geoData] }, // https://deck.gl/#/documentation/deckgl-api-reference/layers/layer?section=data-properties
			onClick: (object) => { if(!this.state.active){this.filterZip3(object)} },
			onHover: (object) => { this.areaHover(object) }
		});

		if(this.state.mapboxtoken !=undefined){
			return (<DeckGL initialViewState={initialViewState} controller={true} layers={[geoLayer]}  >
						<StaticMap mapboxApiAccessToken={this.state.mapboxtoken} mapStyle="mapbox://styles/mapbox/dark-v9"/>
				  </DeckGL>)
		} else {
			return (<DeckGL initialViewState={initialViewState} controller={true} layers={[geoLayer]}  ></DeckGL>)
		}

	}

	// 1k lines in a single .jsx, ooops.
	///// REACT RENDER /////
	render() {

	 	const headerStatus = this.buildHeaderStatus();

	 	const bankselection = this.buildBankList()

	 	const hoveredArea = this.buildAreaHover();

	 	const mapArea = this.buildMap();


	 	// get engine parameter
	 	let engineType = ""
	 	let switchTo = ""
	 	if(this.state.engine === 'cudf'){
	 		engineType = "gpu"
	 		switchTo = "cpu"
	 	} else if(this.state.engine === 'pandas'){
	 		engineType = "cpu"
	 		switchTo = "gpu"
	 	}

	 	// calculate % of data frame shown
	 	let percentDP = 0;
	 	if(this.state.currentDP > 0){
	 		 percentDP = (this.state.currentDP / this.state.totalDP) * 100
	 		percentDP = percentDP.toFixed(2)
	 	}

		return (

			<main className="mapchart">

			    <div className="mapchart-legend-container">

			    	<div className="mapchart-legend-button" onClick={this.switchMode}>switch to {switchTo} engine</div>

	  			    <div className="mapchart-legend-section">
			    		<div className="mapchart-legend-heading">selected bank</div>
						{bankselection}
			    	</div>

			    	<div className="mapchart-legend-section-dial">
			    		<div className="mapchart-legend-section-2col">
				    		<div className="mapchart-legend-heading">opacity</div>
					    	<CircleSlider value={this.state.mapOpacity} onChange={this.mapOpacitySelection} min={10} max={255} stepSize={5}
	        			 	 size={80} circleWidth={5} progressWidth={7} knobRadius={7} circleColor={"gray"} progressColor={"#177be4"} knobColor={"#177be4"} />
	        			 	 <div className="mapchart-circ-value">{this.state.mapOpacity}</div>
			    		</div>
			    		<div className="mapchart-legend-section-2col">
			    		<div className="mapchart-legend-heading">scale</div>
					    	<CircleSlider value={this.state.mapScale} onChange={this.mapScaleSelection} min={1} max={100} stepSize={1}
	        			 	  size={80} circleWidth={5} progressWidth={7} knobRadius={7} circleColor={"gray"} progressColor={"#177be4"} knobColor={"#177be4"} />
	        			 	 <div className="mapchart-circ-value">{this.state.mapScale}</div>
			    		</div>
			    	</div>

	    			<div className="mapchart-legend-section-dial">
			    		<div className="mapchart-legend-section-1col">
			    			<div className="mapchart-legend-heading">dti bins</div>
					    	<CircleSlider value={this.state.chart2Bins} onChange={this.chart2BinSelection} min={1} max={100} stepSize={1}
	        			 	  size={80} circleWidth={5} progressWidth={7} knobRadius={7} circleColor={"gray"} progressColor={"#177be4"} knobColor={"#177be4"} />
	        			 	 <div className="mapchart-circ-value">{this.state.chart2Bins}</div>
			    		</div>
			    	</div>

	    			<div className="mapchart-legend-section-dial">
			    		<div className="mapchart-legend-section-2col">
			    			<div className="mapchart-legend-heading">risk bins</div>
					    	<CircleSlider value={this.state.chart1Bins} onChange={this.chart1BinSelection} min={1} max={100} stepSize={1}
	        			 	 size={80} circleWidth={5} progressWidth={7} knobRadius={7} circleColor={"gray"} progressColor={"#177be4"} knobColor={"#177be4"} />
	        			 	 <div className="mapchart-circ-value">{this.state.chart1Bins}</div>
			    		</div>
			    		<div className="mapchart-legend-section-2col">
				    		<div className="mapchart-legend-heading">credit bins</div>
					    	<CircleSlider  value={this.state.chart3Bins} onChange={this.chart3BinSelection} min={1} max={100} stepSize={1}
		    			 	 size={80} circleWidth={5} progressWidth={7} knobRadius={7} circleColor={"gray"} progressColor={"#177be4"} knobColor={"#177be4"} />
		    			 	 <div className="mapchart-circ-value">{this.state.chart3Bins}</div>
			    		</div>
			    	</div>

			    	<div className="mapchart-legend-section">
			    		<div className="mapchart-legend-heading">portfolio risk score</div>
			    		<ul className="mapchart-key-ul">
			    			<li className="mapchart-key-li"><span className="mapchart-perf mapchart-sel0"></span> <span className="mapchart-perf-title">0.000 - 0.196</span></li>
			    			<li className="mapchart-key-li"><span className="mapchart-perf mapchart-sel1"></span> <span className="mapchart-perf-title">0.196 - 0.198</span></li>
			    			<li className="mapchart-key-li"><span className="mapchart-perf mapchart-sel2"></span> <span className="mapchart-perf-title">0.198 - 0.200</span></li>
			    			<li className="mapchart-key-li"><span className="mapchart-perf mapchart-sel3"></span> <span className="mapchart-perf-title">0.200 - 0.202</span></li>
			    			<li className="mapchart-key-li"><span className="mapchart-perf mapchart-sel4"></span> <span className="mapchart-perf-title">0.202 - 0.2+</span></li>
			    		</ul>
			    		<br/>
			    		<div className="mapchart-legend-heading">total unpaid balance</div>
			    		<span className="mapchart-perf"> <img src="./img/legend-height.png" className="legend-img"/> </span> <div className="mapchart-perf-cube">bar height</div>
			    	</div>

			    	<div className="mapchart-legend-section">
			    		<div className="mapchart-legend-heading">area details</div>
			    		{hoveredArea}
			    	</div>

			    	<div className="mapchart-legend-sink">
						<div className="mapchart-legend-button-small" onClick={this.resetInit}>reset all</div>
					</div>

			    </div>

		   		<div className="mapchart-heading-body">
		   			<div className="mapchart-heading-container">
		   				<div className="mapchart-header-title">	{engineType} aggregated {percentDP}<span className="percent">%</span> of {parseFloat(this.state.totalDP).toLocaleString()} mortgages </div>
		   				{headerStatus}
		   			</div>
		   		</div>

				<div className="mapchart-map-body">
					{mapArea}
				</div>

				<div className="mapchart-chart-body">
					<div className="mapchart-col3-container">
						<BarChart name="chart1" label="portfolio risk score histogram" ratio={0.8} width={700} height={350} tickCount={5} data={this.state.chart1Data} step={0.01} domain={this.state.chart1Domain}  active={this.state.active} onSelection={this.filterCharts}  />
						<div className="mapChart-chart-reset" onClick={() => {this.resetChartFilter('chart1')}}> reset </div>
					</div>
					<div className="mapchart-col3-container">
						<BarChart name="chart2" label="debt to income histogram" ratio={0.8} width={700} height={350} tickCount={5} data={this.state.chart2Data} step={1} domain={this.state.chart2Domain} active={this.state.active} onSelection={this.filterCharts} />
						<div className="mapChart-chart-reset" onClick={() => {this.resetChartFilter('chart2')}}> reset </div>
					</div>
					<div className="mapchart-col3-container">
						<BarChart name="chart3" label="credit score histogram" ratio={0.8} width={700} height={350} tickCount={5} data={this.state.chart3Data} step={50} domain={this.state.chart3Domain} active={this.state.active} onSelection={this.filterCharts}  />
						<div className="mapChart-chart-reset" onClick={() => {this.resetChartFilter('chart3')}}> reset </div>
					</div>
				</div>


			</main>
		)
	}
}

export default MapChart;
