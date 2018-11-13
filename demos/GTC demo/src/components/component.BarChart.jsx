import React, { Component, PureComponent } from "react";

// https://formidable.com/open-source/victory/docs/victory-chart/
import { VictoryBar, VictoryChart, VictoryAxis, VictoryBrushContainer } from 'victory';

// Pure component to reduce render calls
// https://reactjs.org/docs/react-api.html#reactpurecomponent
class BarChart extends React.PureComponent {
	constructor(props) {
		super(props);
		this.state = {
			name: undefined,
		}

		this.callFilter = this.debounce(this.callFilter.bind(this), 150)

	}

	componentDidMount() {

		this.setState({
			name: this.props.name
		})

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

	// call parent chart filter
	callFilter(domain, props){
		this.props.onSelection(domain, props)
	}


	render() {

		// Note: active is to prevent interactions while data is selling being processed. Domain is to prevent odd brushDomain behavior. brushDomain is only sent from parent to keep selection domain on bin size update.	
		const  {name, ratio, width, height, tickCount, label, data, domain, active, brushDomain, onSelection} = this.props	

		// Note: gradient just for subtle bar effect
		return (<div>
					<svg style={{ height: '0', width: '0' }}>
						<defs>	
						  <linearGradient id="chartGradient" x1="0%" y1="100%" x2="0%" y2="0%">
						    <stop offset="0%" style={{stopColor:"rgb(200, 200, 200)", stopOpacity:1}}/>
						    <stop offset="100%" style={{stopColor:"rgb(255,255,255)", stopOpacity:1}}/>
						  </linearGradient>
						</defs>
					</svg>
					<br/>
					<VictoryChart
						style={{parent:{position:"absolute"}}}
						domainPadding={{x: 40*ratio}}
						domain={{x:domain}}
						padding={{left: 60*ratio, right: 40*ratio, top: 20*ratio, bottom: 120*ratio}}
						width={width} height={height}
					 	containerComponent={
					 						<VictoryBrushContainer
					 						  allowDrag={false}
					 						  disable={active}
										      brushDimension="x"
										      defaultBrushArea="all"
											  brushDomain={{x: brushDomain}} 
										      onBrushDomainChange={(domain, props) => { this.callFilter(domain, props) }}
										      brushStyle={{stroke: "transparent", fill: "white", fillOpacity: 0.1}}
										    />										
											} 
					 	animate={{ duration: 250, easing: "quadInOut" }} >
						
						<VictoryBar 
							name={name}
							data={data}
							alignment="start"
							style={{ data: {fill: (d, active) => active ? "rgb(8,81,156)" : "url(#chartGradient)"} }} 
							x="x" y="y" 
						/>

						<VictoryAxis dependentAxis 
									 tickFormat={(t) => {return (`${parseFloat(t)/1000}K`)}}
				     				 style={{
				     				 		axis: {strokeWidth: 0},
				     				 		grid: {stroke: "rgba(255,255,255,0.2)", strokeWidth: 1},
				     				 		tickLabels: {fontSize: 15*ratio, fill: "white", padding: 10}
				     				 		}}
				    	/>

				     	<VictoryAxis label={label}
				     				 tickCount={tickCount}
				     				 tickFormat={(t) => {return (t)}}
				     				 style={{
				     				 		axis: {stroke: "white"}, 
				     				 		axisLabel: {fontFamily:"'Cabin', sans-serif", fontVariant:"small-caps", padding: 30*ratio, fontSize: 30*ratio, fill: "white"}, 
				     				 		ticks: {stroke: "gray", size: 4},
				     				 		tickLabels: {fontSize: 15*ratio, fill: "white", padding: 5}
				     				 		}} 
				     	/>

					</VictoryChart>
				</div>
			)
	}
}

export default BarChart;