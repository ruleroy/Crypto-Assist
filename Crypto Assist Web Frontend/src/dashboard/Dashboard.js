import React, {Component} from 'react';
import {Redirect} from 'react-router-dom';
class Dashboard extends Component {

	constructor(props){
		super(props);
		this.state = {
			name:'',
			redirect: false,
		};
	}

	componentDidMount() {
		let data = JSON.parse(sessionStorage.getItem('userData'));
		console.log(data);
		this.setState({name: data.name});
	}

	render() {

		if(!sessionStorage.getItem('userData') || this.state.redirect){
			return (<Redirect to={'/'}/>);
		}

		return (
			<div >
			Welcome {this.state.name}
			</div>
			);
	}
}
export default Dashboard;