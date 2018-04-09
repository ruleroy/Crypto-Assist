import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import Dashboard from './dashboard/Dashboard'
import registerServiceWorker from './registerServiceWorker';
import { Route, BrowserRouter, Switch } from 'react-router-dom';
import { Provider } from 'react-redux';



ReactDOM.render(

	<BrowserRouter>
		<Switch>
		<Route exact path="/" component={App} />
		<Route path="/dashboard" component={Dashboard} />
		</Switch>
	</BrowserRouter>


	, document.getElementById('root'));
registerServiceWorker();
