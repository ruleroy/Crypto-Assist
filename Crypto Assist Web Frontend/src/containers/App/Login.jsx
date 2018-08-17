import React, { Component } from 'react';
import {
    Route,
    Switch,
    Redirect
} from 'react-router-dom';
import NotificationSystem from 'react-notification-system';

import { GoogleLogin } from 'react-google-login';

import Header from 'components/Header/Header';
import Footer from 'components/Footer/Footer';
import Sidebar from 'components/Sidebar/Sidebar';

import {style} from "variables/Variables.jsx";

import appRoutes from 'routes/app.jsx';

import 'assets/css/login.css'
import logo from 'assets/img/cryptoassist.png';
import googlelogo from 'assets/img/googlelogowhite.png';

class App extends Component {
    constructor(props){
        super(props);
        this.componentDidMount = this.componentDidMount.bind(this);
        this.handleNotificationClick = this.handleNotificationClick.bind(this);
        this.signup = this.signup.bind(this);

        this.state = {
            _notificationSystem: null,
            redirect: false,
            loginError: false
        };

    }
    handleNotificationClick(position){
        var color = Math.floor((Math.random() * 4) + 1);
        var level;
        switch (color) {
            case 1:
            level = 'success';
            break;
            case 2:
            level = 'warning';
            break;
            case 3:
            level = 'error';
            break;
            case 4:
            level = 'info';
            break;
            default:
            break;
        }
        this.state._notificationSystem.addNotification({
            title: (<span data-notify="icon" className="pe-7s-gift"></span>),
            message: (
                <div>
                Welcome to <b>Light Bootstrap Dashboard</b> - a beautiful freebie for every web developer.
                </div>
                ),
            level: level,
            position: position,
            autoDismiss: 15,
        });
    }

    signup(res, type){
        let postData;
        if(type === 'google' && res.w3.U3) {
          postData = {
            name: res.w3.ig,
            provider: type,
            email: res.w3.U3,
            provider_id: res.El,
            token: res.Zi.access_token,
            provider_pic: res.w3.Paa
        };
    }

    if(postData) {
     sessionStorage.setItem("userData", JSON.stringify(postData));
     this.setState({redirect: true});
 }
}

componentDidMount(){
    document.title = "Crypto Assist - Dashboard";
}

componentDidUpdate(e){
    if(window.innerWidth < 993 && e.history.location.pathname !== e.location.pathname && document.documentElement.className.indexOf('nav-open') !== -1){
        document.documentElement.classList.toggle('nav-open');
    }
}
render() {
    if(this.state.redirect || sessionStorage.getItem('userData')) {
        return (<Redirect to={'/dashboard'}/>)
    }

    const responseGoogle = (response) => {
        console.log(response);
        this.signup(response, 'google');
    }

    return (

    <div className="wrapper">
    <div className="login">
    <img src={logo} id="center" />
    <GoogleLogin
    className="login-google"
    clientId="519974987916-u6uhj7r3qco67rf0js4kear8tpt7e3de.apps.googleusercontent.com"
    buttonText=""
    onSuccess={responseGoogle}
    onFailure={responseGoogle}
    />
    </div>
    </div>
    );
}
}

export default App;
