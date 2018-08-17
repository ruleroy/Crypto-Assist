import React, { Component } from 'react';
import {
    Grid, Row, Col,
    FormGroup, ControlLabel, FormControl, Table
} from 'react-bootstrap';

import {Card} from 'components/Card/Card.jsx';
import {FormInputs} from 'components/FormInputs/FormInputs.jsx';
import {UserCard} from 'components/UserCard/UserCard.jsx';
import {StatsCard} from 'components/StatsCard/StatsCard.jsx';
import Button from 'elements/CustomButton/CustomButton.jsx';

import {LineChart, Brush, 
    Scatter, ScatterChart, Line, XAxis, YAxis, ZAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

    import avatar from "assets/img/faces/face-3.jpg";
    import heatmapImg from "assets/img/graph.png";
    import Intl from 'intl';
    import Loader from 'react-loader';

    class AnalyzeMarket extends Component {
        constructor(props){
            super(props);
            this.analyzeCoin = this.analyzeCoin.bind(this);
            this.getTop10 = this.getTop10.bind(this);
            this.getGlobal = this.getGlobal.bind(this);
            this.refreshHeatmap = this.refreshHeatmap.bind(this);
            this.handleChange = this.handleChange.bind(this);
            this.state = {
                top10: [],
                tdArray: [],
                btcPercentage: 0,
                totalMarketCap: 0,
                total24hVol: 0,
                analyze: false,
                selectedValue: 'BTC',
                arrOption: [],
                analyzeChartData: [],
                analyzeChartDataLinear: [],
                analyzeChartCoin: '',
                loadedChart: true,
                trend: 'Neutral',
                analyzeChartDataPrediction: [],
                analyzeChartDataReal: [],
                accuracy: ''
            }
        }

        getGlobal(){
            var that = this;
            var coinMarketCapAPI = new Request('https://api.coinmarketcap.com/v1/global/', {
                method: 'GET'
            });

            fetch(coinMarketCapAPI)
            .then(function(response){
                if(response.status === 200){
                    response.json()
                    .then(function(data){

                        that.setState({
                            btcPercentage: data.bitcoin_percentage_of_market_cap + "%",
                            totalMarketCap: "$" + parseInt(data.total_market_cap_usd).toLocaleString(),
                            total24hVol: "$" + parseInt(data.total_24h_volume_usd).toLocaleString()
                        });
                        console.log(data);
                    });
                } else if(response.status === 400) {
                    alert('error');
                }
            });
        }


        getTop10(){
            var that = this;
            var coinMarketCapAPI = new Request('https://api.coinmarketcap.com/v1/ticker/?limit=10', {
                method: 'GET'
            });

            fetch(coinMarketCapAPI)
            .then(function(response){
                if(response.status === 200){
                    response.json()
                    .then(function(data){
                        var i;
                        var top = [];
                        for (i = 0; i< data.length; i++){
                            top.push(data[i].symbol);
                        }

                        var arr = [];
                        for (i = 0; i< data.length; i++){
                            var coin = [];
                            coin.push(data[i].rank);
                            coin.push(data[i].name);
                            coin.push("$" + data[i].price_usd);
                            coin.push("$" + parseInt(data[i].market_cap_usd).toLocaleString());
                            coin.push(data[i].percent_change_24h + "%");
                            arr.push(coin);
                        }

                        that.setState({
                            top10: data,
                            tdArray: arr
                        });

                        var arr2 = [];
                        for (var k = 0; k < top.length; k++) {
                            arr2.push(<option key={k} value={top[k]}> {top[k]} </option>);
                        }
                        that.setState({
                          arrOption: arr2
                      });

                        console.log(data);
                        console.log(top);
                    });
                } else if(response.status === 400) {
                    alert('error');
                }
            });
        }

        refreshHeatmap(){
            var that = this;
            var getHeatmap = new Request('http://localhost:3001/api/get-charts?pair=BTCUSDT', {
                method: 'GET'
            });

            fetch(getHeatmap)
            .then(function(response){
                if(response.status === 200){
                    response.json()
                    .then(function(data){
                        console.log(data)
                    });
                } else if(response.status === 400) {
                    alert('error');
                }
            });
        }

        handleChange(e){
            this.setState({selectedValue: e.target.value});
        }

        analyzeCoin(){
            var that = this;
            var getHeatmap = new Request('http://localhost:3001/api/get-analyze-coin?pair='+this.state.selectedValue, {
                method: 'GET'
            });

            fetch(getHeatmap)
            .then(function(response){
                if(response.status === 200){
                    response.json()
                    .then(function(data){
                        var arr = [];
                        var arr2 = [];
                        var pred = [];
                        var real = [];
                        for (var i = 0; i< 100; i++){
                            var obj = {
                                time: data[i].time,
                                price: data[i].price
                            };
                            var obj2 = {
                                time: data[i].time,
                                price: data[i].linearY
                            };

                            arr.push(obj);
                            arr2.push(obj2);
                        }
                        for (var j = data.length-31; j< data.length-1; j++){
                            var obj3 = {
                                time: data[j].ptime,
                                price: data[j].prediction
                            };
                            
                            pred.push(obj3);
                            
                        }
                        for (var k = data.length-61; k< data.length-31; k++){
                            var obj4 = {
                                time: data[k].rtime,
                                price: data[k].rprice
                            };
                            real.push(obj4);
                        }

                        var eqn = arr2[0].price - arr2[arr2.length-1].price
                        var trend = 'Neutral'
                        console.log(eqn)
                        if(eqn < 0){
                            trend = 'Uptrend'
                        } else if (eqn > 0){
                            trend = 'Downtrend'
                        } else if (eqn === 0){
                            trend = 'Neutral'
                        }

                        var coin = that.state.selectedValue;
                        if(coin === "BTC"){
                            coin = coin + "/USDT"
                        } else {
                            coin = coin + "/BTC"
                        }

                        that.setState({
                          analyzeChartData: arr,
                          analyzeChartDataLinear: arr2,
                          analyzeChartDataPrediction: pred,
                          analyzeChartDataReal: real,
                          analyzeChartCoin: coin,
                          loadedChart: true,
                          trend: trend,
                          accuracy: data[data.length-1].accuracy + "%"
                      });
                        console.log(arr);
                        console.log(arr2);
                        console.log("pred:");
                        console.log(that.state.analyzeChartDataPrediction);
                        console.log("real:");
                        console.log(that.state.analyzeChartDataReal);
                        console.log(eqn);
                        console.log(trend);
                        console.log(that.state.accuracy);
                    });
                } else if(response.status === 400) {
                    alert('error');
                }
            });

            this.setState({analyze: true, loadedChart: false});
            console.log(this.state.selectedValue);
        }

        componentDidMount(){
            document.title = "Crypto Assist - Analyze Market";
            this.getTop10();
            this.getGlobal();
            this.refreshHeatmap();
        }


        render() {
            var thArray = ["Rank", "Name", "Price", "Market Cap", "Change (24h)"];
            const RenderNoShape = (props)=>{ 
             return null; 
         }

         return (
            <div className="content">
            <Grid fluid>

            <Row>
            <Col md = {12}>
            <Card
            title="Global Statistics"
            content=
            {
                <Row>
                <Col md = {4}>
                <StatsCard
                bigIcon={<i className="pe-7s-display2 text-success"></i>}
                statsText="Total Market Cap"
                statsValue=
                {
                    <div>
                    <p>{this.state.totalMarketCap}</p>
                    </div>
                }
                />
                </Col>
                <Col md = {4}>
                <StatsCard
                bigIcon={<i className="pe-7s-graph2 text-warning"></i>}
                statsText="Total 24 Hour Volume"
                statsValue=
                {
                    <div>
                    <p>{this.state.total24hVol}</p>
                    </div>
                }
                />
                </Col>
                <Col md = {4}>
                <StatsCard
                bigIcon={<i className="pe-7s-graph1 text-danger"></i>}
                statsText="BTC Percentage Of Market Cap"
                statsValue=
                {
                    <div>
                    <p>{this.state.btcPercentage}</p>
                    </div>
                }
                />
                </Col>
                </Row>
            }
            />
            </Col>
            </Row>

            <Row>
            <Col md={7}>
            <Card
            title="Current Top 10 Cryptocurrencies by Market Cap"
            content=
            {
                <Table striped hover>
                <thead>
                <tr>
                {

                    thArray.map((prop, key) => {
                        return (
                            <th  key={key}>{prop}</th>
                            );
                    })
                }
                </tr>
                </thead>
                <tbody>
                {
                    this.state.tdArray.map((prop,key) => {
                        return (
                            <tr key={key}>
                            {
                                prop.map((prop,key)=> {
                                    return (
                                        <td  key={key}>
                                        {
                                            key === 4 && prop.includes("-")
                                            ?
                                            <font color='red'>{prop}</font>
                                            :
                                            null
                                        }
                                        {
                                            key === 4 && !prop.includes("-")
                                            ?
                                            <font color='green'>{prop}</font>
                                            :
                                            null
                                        }
                                        {
                                            key === 4
                                            ?
                                            null
                                            :
                                            <div>{prop}</div>
                                        }

                                        </td>
                                        );
                                })
                            }
                            </tr>
                            )
                    })
                }
                </tbody>
                </Table>
            }
            />
            </Col>
            <Col md={5}>
            <Card
            title="Top 10 Correlation Heatmap"
            content=
            {
                <div>
                <img src={heatmapImg} alt=""/>
                </div>
            }
            />
            </Col>
            </Row>
            <Row>
            <Col md={12}>
            <Card
            title="Single Coin Analyze"
            content=
            {
                <div>
                <Row>
                <Col md={7}>
                <FormGroup controlId="formControlsSelect">
                <ControlLabel>Select coin</ControlLabel>
                <FormControl componentClass="select" placeholder="select" onChange={this.handleChange} value={this.state.selectedValue}>
                {this.state.arrOption}
                </FormControl>
                </FormGroup>
                </Col>

                <Col md={5}>
                <Loader loaded={this.state.loadedChart}>
                <Button className="analyze-coin" bsStyle="primary" onClick={this.analyzeCoin}>Analyze Coin</Button>
                </Loader>
                </Col>
                </Row>

                {
                    this.state.analyze
                    ?
                    <h4 id="center">Current {this.state.analyzeChartCoin} Trend:&nbsp;
                    {
                        this.state.trend === 'Uptrend'
                        ?
                        <font color="green"><b>{this.state.trend}</b></font>
                        : null
                    }
                    {
                        this.state.trend === 'Neutral'
                        ?
                        <font color="gray"><b>{this.state.trend}</b></font>
                        : null
                    }
                    {
                        this.state.trend === 'Downtrend'
                        ?
                        <font color="red"><b>{this.state.trend}</b></font>
                        : null
                    }
                    </h4>
                    :
                    null
                }
                {
                    this.state.analyze
                    ?
                    <div>
                    <ResponsiveContainer width="97%" height="30%">
                    <ScatterChart width={730} height={250}
                    margin={{ top: 20, right: 20, bottom: 10, left: 40 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" label={{value: "Time", position: 'insideBottomLeft', offset: 0}} 
                    dataKey="time" name="Time" domain={['auto', 'auto']}/>
                    <YAxis type="number" label={{value: "Price", angle: -90, position: 'left', offset: 0}}
                    dataKey="price" name="Price" domain={['auto', 'auto']}/>
                    <ZAxis range={[100]}/>
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                    <Legend />
                    <Scatter name={this.state.analyzeChartCoin} data={this.state.analyzeChartData} fill="#8884d8"/>
                    <Scatter name="Linear Regression Line" data={this.state.analyzeChartDataLinear} line fill="#971C5B" shape={<RenderNoShape />}/>
                    </ScatterChart>
                    </ResponsiveContainer>
                    </div>
                    :
                    null
                }
                {
                    this.state.analyze
                    ?
                    <div>
                    <br/>
                    <h4 id="center">Linear Regression Model Prediction (4HR Timeframe)</h4>
                    <ResponsiveContainer width="97%" height="30%">
                    <ScatterChart width={730} height={250}
                    margin={{ top: 20, right: 20, bottom: 10, left: 40 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis allowDataOverflow={true} type="number" label={{value: "Time", position: 'insideBottomLeft', offset: 0}} 
                    dataKey="time" name="Time" domain={[470, 530]}/>
                    <YAxis type="number" label={{value: "Price", angle: -90, position: 'left', offset: 0}}
                    dataKey="price" name="Price" domain={['auto', 'auto']}/>
                    <ZAxis range={[30]}/>
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                    <Legend />
                    <Scatter name={this.state.analyzeChartCoin} data={this.state.analyzeChartDataReal} line fill="#8884d8"/>
                    <Scatter name="Prediction" data={this.state.analyzeChartDataPrediction} line fill="#971C5B" 
                    shape="circle"/>
                    </ScatterChart>
                    </ResponsiveContainer>
                    <h5 id="center">Model accuracy: {this.state.accuracy}</h5>
                    <br/>
                    </div>
                    :
                    null
                }
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

export default AnalyzeMarket;
