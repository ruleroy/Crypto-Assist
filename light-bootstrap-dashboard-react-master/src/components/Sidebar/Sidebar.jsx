import React, {Component} from 'react';
import { NavLink } from 'react-router-dom';

import HeaderLinks from '../Header/HeaderLinks.jsx';

import imagine from 'assets/img/sidebar.jpg';
import logo from 'assets/img/ca.png';

import appRoutes from 'routes/app.jsx';
import {UserCard} from 'components/UserCard/UserCard.jsx';

class Sidebar extends Component{
    constructor(props){
        super(props);
        this.state = {
            width: window.innerWidth
        }
    }
    activeRoute(routeName) {
        return this.props.location.pathname.indexOf(routeName) > -1 ? 'active' : '';
    }
    updateDimensions(){
        this.setState({width:window.innerWidth});
    }
    componentDidMount() {
        this.updateDimensions();
        let data = JSON.parse(sessionStorage.getItem('userData'));
        console.log(data);
        this.setState({
            name: data.name,
            username: data.email,
            pic: data.provider_pic
        });
        window.addEventListener("resize", this.updateDimensions.bind(this));
    }
    render(){
        const sidebarBackground = {
            backgroundImage: 'url(' + imagine + ')'
        };
        return (
            <div id="sidebar" className="sidebar" data-color="black" data-image={imagine}>
            <div className="sidebar-background" style={sidebarBackground}></div>
            <div className="logo">
            <a href="#" className="simple-text logo-mini">
            <div className="logo-img">
            <img src={logo} alt="logo_image"/>
            </div>

            </a>
            <a href="#" className="simple-text logo-normal">
            Crypto Assist
            </a>
            </div>
            <div className="sidebar-wrapper">
            <UserCard
            bgImage="https://ununsplash.imgix.net/photo-1431578500526-4d9613015464?fit=crop&fm=jpg&h=300&q=75&w=400"
            avatar={this.state.pic}
            name={this.state.name}
            userName={this.state.username}
            />
            <ul className="nav">
            { this.state.width <= 991 ? (<HeaderLinks />):null }
            {
                appRoutes.map((prop,key) => {
                    if(!prop.redirect)
                        return (
                            <li key={key}>
                            <NavLink to={prop.path} className="nav-link" activeClassName="active">
                            <i className={prop.icon}></i>
                            <p>{prop.name}</p>
                            </NavLink>
                            </li>
                            );
                    return null;
                })
            }
            </ul>
            </div>
            </div>
            );
    }
}

export default Sidebar;
