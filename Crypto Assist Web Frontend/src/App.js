import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import CryptoCheck from './CryptoCheck.js';
import GoogleLogin from 'react-google-login';
import {Redirect} from 'react-router-dom';

class App extends Component {
  constructor(props){
    super(props);
    this.state = {
      redirect: false,
      loginError: false
    };
    this.signup = this.signup.bind(this);
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

 render() {
  if(this.state.redirect || sessionStorage.getItem('userData')) {
    return (<Redirect to={'/dashboard'}/>)
  }

  const responseGoogle = (response) => {
    console.log(response);
    this.signup(response, 'google');
  }

  return (
    <div className="App">
    <header className="App-header">
    <img src={logo} className="App-logo" alt="logo" />
    <h1 className="App-title">Welcome to React</h1>
    </header>
    <p className="App-intro">
    To get started, edit <code>src/App.js</code> and save to reload.
    </p>


    <GoogleLogin
    clientId="519974987916-u6uhj7r3qco67rf0js4kear8tpt7e3de.apps.googleusercontent.com"
    buttonText="Login"
    onSuccess={responseGoogle}
    onFailure={responseGoogle}
    />

    <CryptoCheck crypto="hi"/>
    </div>
    );
}
}

export default App;
