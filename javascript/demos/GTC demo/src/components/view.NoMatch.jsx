 import React, { Component } from "react";
import styles from "./scss/nomatch";

class NoMatch extends React.Component {
	constructor(props) {
		super(props);
	}

	/* so nav click always moves to top of page */
	componentDidMount() {
		window.scrollTo(0, 0);
	}

	render() {
		return (
			<h1>Sorry could not find page.</h1>
		)
	}
}

export default NoMatch;