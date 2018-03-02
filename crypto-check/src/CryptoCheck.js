import React, { Component } from 'react';
import {Panel} from 'react-bootstrap';
import './CryptoCheck.css';

class CryptoCheck extends Component {
	constructor(props){
		super(props);

		this.createCryptoCheck = this.createCryptoCheck.bind(this);
	}

	createCryptoCheck(crypto){
		return (
			<div>
			<Panel className="cryptoFormat">
			<Panel.Body><h1>{crypto}</h1>
			</Panel.Body>
			</Panel>
			
			</div>
			);
	}

	render(){

		return this.createCryptoCheck(
			this.props.crypto
			);
	}
}

export default CryptoCheck;