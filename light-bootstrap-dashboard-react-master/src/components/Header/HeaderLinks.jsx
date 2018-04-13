import React, {Component} from 'react';
import { NavItem, Nav, NavDropdown, MenuItem } from 'react-bootstrap';
import {
    Route,
    Switch,
    Redirect
} from 'react-router-dom';


class HeaderLinks extends Component{
    constructor(props){
        super(props);
        this.logout = this.logout.bind(this);
    }


  handleSelect(eventKey) {
    //alert(`selected ${eventKey}`);
    if(eventKey == 3){
        this.logout();
    }
}

logout(){
    sessionStorage.removeItem("userData");
    window.location.reload();
}

render(){
    const notification = (
        <div>
        <i className="fa fa-globe"></i>
        <b className="caret"></b>
        <span className="notification">5</span>
        <p className="hidden-lg hidden-md">Notification</p>
        </div>
        );

    return (
        <div>

        <Nav pullRight>
        <NavItem eventKey={1} href="#">Account</NavItem>

        <NavItem eventKey={3} href="#" onSelect={this.handleSelect.bind(this)}>Log out</NavItem>
        </Nav>
        </div>
        );
}
}

export default HeaderLinks;
