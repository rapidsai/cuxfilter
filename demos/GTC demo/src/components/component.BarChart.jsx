import React, { Component, PureComponent } from "react";

// https://formidable.com/open-source/victory/docs/victory-chart/
import { VictoryBar, VictoryChart, VictoryAxis } from 'victory';

// https://github.com/davidchin/react-input-range
import InputRange from 'react-input-range';

import './scss/barchart-style'

// Pure component to reduce render calls
// https://reactjs.org/docs/react-api.html#reactpurecomponent
class BarChart extends React.PureComponent {
	constructor(props) {
		super(props);
		this.state = {
			selection: { min: 0, max: 0 }
		}

	}

	componentDidUpdate(prevProps) {
	  // Typical usage (don't forget to compare props):
	  // on ininital load, set selection range to max and min

	  if (this.props.domain !== prevProps.domain && this.props.domain != undefined ) {
	    	
	    	console.log("Range Slider set to max-min domain...", this.props.domain.min, this.props.domain.max)
	    	this.setState({
	    		selection: { min: this.props.domain.min, max: this.props.domain.max}
	    	})

	  }
	}


	render() {

		// Note: active is to prevent interactions while data is still being processed.
		let  {name, ratio, width, height, tickCount, label, data, step, domain, active, onSelection} = this.props

		if(domain === undefined){
			domain = {min:0, max:1}
		}

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

						domainPadding={{x: 40*ratio}}
						padding={{left: 60*ratio, right: 40*ratio, top: 20*ratio, bottom: 120*ratio}}
						width={width} height={height}
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
				    <InputRange
				    	name={name}
				    	step={step}
				        disabled={active}
				        formatLabel={selection => selection.toFixed(2)}
				        draggableTrack={true}
				        minValue={domain.min}
				        maxValue={domain.max}
				        value={this.state.selection}
				        onChange={selection => this.setState({ selection })}
				        onChangeComplete={selection => { onSelection(selection, name) }}
				    />
				</div>
			)
	}
}

export default BarChart;