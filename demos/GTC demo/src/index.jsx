import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import { HashRouter, Switch, Route } from 'react-router-dom';

// global styles
import './components/scss/global-style';


import MapChart from './components/view.MapChart';
import NoMatch from './components/view.NoMatch';


// Note: routes added for future flexibility
class Root extends React.Component {

	render(){

		return(
				<HashRouter hashType="noslash">
					<Switch>
						<Route exact path="/" component={MapChart} />						
						<Route component={NoMatch} />
					</Switch>
				</HashRouter>
			)
	}
}

ReactDOM.render(
	<Root />,
	document.getElementById("root")
)
