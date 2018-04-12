import React from 'react';
import ReactDOM from 'react-dom';

import {
	HashRouter,
	Route,
	Switch
} from 'react-router-dom';

import App from 'containers/App/App.jsx';
import Login from 'containers/App/Login.jsx';

import './assets/css/bootstrap.min.css';
import './assets/css/animate.min.css';
import './assets/sass/light-bootstrap-dashboard.css';
import './assets/css/demo.css';
import './assets/css/pe-icon-7-stroke.css';




ReactDOM.render((
	<HashRouter>
	<Switch>
	<Route exact path="/" name="Login" component={Login}/>
	<Route path="/" name="Dashboard" component={App}/>
	</Switch>
	</HashRouter>
	),document.getElementById('root'));
