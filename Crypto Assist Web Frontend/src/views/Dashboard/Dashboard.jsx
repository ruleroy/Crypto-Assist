import React, { Component } from 'react';
import ChartistGraph from 'react-chartist';
import { Grid, Row, Col, Panel} from 'react-bootstrap';

import {UserCard} from 'components/UserCard/UserCard.jsx';
import Button from 'elements/CustomButton/CustomButton.jsx';

import {LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

import avatar from "assets/img/faces/face-0.jpg";
import {Card} from 'components/Card/Card.jsx';
import {StatsCard} from 'components/StatsCard/StatsCard.jsx';
import {Tasks} from 'components/Tasks/Tasks.jsx';
import {
    dataPie,
    legendPie,
    dataSales,
    optionsSales,
    responsiveSales,
    legendSales,
    dataBar,
    optionsBar,
    responsiveBar,
    legendBar
} from 'variables/Variables.jsx';

import Loader from 'react-loader';

class Dashboard extends Component {
    constructor(props){
        super(props);
        this.getBinanceData = this.getBinanceData.bind(this);
        this.getBinanceAccData = this.getBinanceAccData.bind(this);
        this.getChartData = this.getChartData.bind(this);
        this.state = {
            open: false,
            status: 'Updating...',
            loadedAcc: false,
            loadedGraph: false,
            name: '-',
            username: '-',
            pic: '',
            pair: 'BTCUSDT',
            data: {},
            data2: [],
            btc_bal: '-',
            total_btc_val: '-',
            total_usd_val: '-',
            btc_price: '0.00',
            optionsSales: {
              low: 0,
              high: 50,
              showArea: false,
              height: "270px",
              axisX: {showGrid: true},
              lineSmooth: false,
              showLine: true,
              showPoint: true,
              fullWidth: false,
              chartPadding: {right: 30, left: 30, bottom: 30}
          }
      };
  }

  getBinanceData(){
    var that = this;
    var getData = new Request('http://localhost:3001/api/get-data?pair=' + this.state.pair, {
        method: 'GET'
    });

    fetch(getData)
    .then(function(response){
        if(response.status === 200){
            response.json()
            .then(function(data){
                        //alert('success');
                        //console.log(data);
                        let optionsSales = {...that.state.optionsSales};
                        optionsSales.low = data.lowest;
                        optionsSales.high = data.highest;
                        that.setState({
                            loadedGraph: true,
                            data: data,
                            optionsSales
                        });
                        //console.log(that.state.data);
                    });
        } else if(response.status === 400) {
            alert('error');
        }
    });
}

getChartData(){
    var that = this;
    var getData = new Request('http://localhost:3001/api/get-data2?pair=' + this.state.pair, {
        method: 'GET'
    });

    fetch(getData)
    .then(function(response){
        if(response.status === 200){
            response.json()
            .then(function(data){
                that.setState({
                    loadedGraph: true,
                    data2: data
                });
            });
        } else if(response.status === 400) {
            alert('error');
        }
    });
}

getBinanceAccData(){
    var that = this;
    var getAccData = new Request('http://localhost:3001/api/get-acc', {
        method: 'GET'
    });

    fetch(getAccData)
    .then(function(response){
        if(response.status === 200){
            response.json()
            .then(function(data){
                that.setState({
                    status: 'Updated now',
                    loadedAcc: true,
                    btc_bal : data.btc_bal,
                    total_usd_val: data.total_usd_val,
                    total_btc_val: data.total_btc_val,
                    btc_price: data.btc_price
                });
                console.log(data);
            });
        } else if(response.status === 400) {
            alert('error');
        }
    });
}

componentDidMount(){
    document.title = "Crypto Assist - Dashboard";
    let data = JSON.parse(sessionStorage.getItem('userData'));
    console.log(data);
    this.setState({
        name: data.name,
        username: data.email,
        pic: data.provider_pic
    });
    this.getBinanceAccData();
    //this.getBinanceData();
    this.getChartData();
}

createLegend(json){
    var legend = [];
    for(var i = 0; i < json["names"].length; i++){
        var type = "fa fa-circle text-"+json["types"][i];
        legend.push(
            <i className={type} key={i}></i>
            );
        legend.push(" ");
        legend.push(
            json["names"][i]
            );
    }
    return legend;
}
render() {
    return (
        <div className="content">
        <Grid fluid>
        <Row>
        {
            /*
        <Col lg={3} sm={6}>

        <UserCard
        bgImage="https://ununsplash.imgix.net/photo-1431578500526-4d9613015464?fit=crop&fm=jpg&h=300&q=75&w=400"
        avatar={this.state.pic}
        name={this.state.name}
        userName={this.state.username}
        />
        </Col>
        */
    }
    <Col lg={4} sm={6}>

    <StatsCard
    bigIcon={<i className="pe-7s-server text-warning"></i>}
    statsText="BTC Balance"
    statsValue={<Loader loaded={this.state.loadedAcc}>{this.state.btc_bal}</Loader>}
    statsIcon={<i className="fa fa-refresh"></i>}
    statsIconText={this.state.status}
    />

    </Col>
    <Col lg={4} sm={6}>

    <StatsCard
    bigIcon={<i className="pe-7s-wallet text-danger"></i>}
    statsText="Portfolio Value (BTC)"
    statsValue={<Loader loaded={this.state.loadedAcc}>{this.state.total_btc_val}</Loader>}
    statsIcon={<i className="fa fa-refresh"></i>}
    statsIconText={this.state.status}
    />

    </Col>
    <Col lg={4} sm={6}>

    <StatsCard
    bigIcon={<i className="pe-7s-cash text-success"></i>}
    statsText="Portfolio Value (USD)"
    statsValue={<Loader loaded={this.state.loadedAcc}>{"$" + this.state.total_usd_val}</Loader>}
    statsIcon={<i className="fa fa-refresh"></i>}
    statsIconText={this.state.status}
    />

    </Col>
    </Row>
    <Row>
    <Col md={12}>
    
    <Card
    statsIcon="fa fa-history"
    id="chartHours"
    title=
    {
        <div>
        <Row>
        <Col xs={1}>
        <div className="icon-big-pair text-center">
        <i className="pe-7s-cash text-success bold"></i>
        </div>
        </Col>
        
        <Col xs={11}>
        <p>BTC / USDT</p>
        <h2 id="price-text"><Loader loaded={this.state.loadedAcc}>{"$" + this.state.btc_price}</Loader></h2>
        </Col>
        </Row>
        </div>
    }
    category={<span className="time-frame text-center">Binance - 4 Hour Time Frame</span>}
    stats={this.state.status}
    content=
    {
        <div>


        <Row>
        <ResponsiveContainer width="97%" height="30%">
        <LineChart data={this.state.data2}
        margin={{top: 5, right: 30, left: 20, bottom: 20}}>
        <XAxis dataKey="date"/>
        <YAxis type="number" domain={['auto', 'auto']} />
        <CartesianGrid strokeDasharray="3 3"/>
        <Tooltip/>
        <Line type="linear" dataKey="price" stroke="#8884d8" activeDot={{r: 8}}/>
        </LineChart>
        </ResponsiveContainer>
        </Row>

        </div>
    }

    />
    </Col>

    </Row>


    </Grid>
    </div>
    );
}
}

export default Dashboard;
