/* ============================================================
 * node-binance-api
 * https://github.com/jaggedsoft/node-binance-api
 * ============================================================
 * Copyright 2017-, Jon Eyrick
 * Released under the MIT License
 * ============================================================ */

"use strict";

var path = require( "path" );
var assert = require( "assert" ).strict;
var binance = require( path.resolve( __dirname, "node-binance-api.js" ) );
var util = require( "util" );

var num_pairs = 299;
var num_currencies = 156;

function debug( x ) {
  console.log( typeof x );
  console.log( util.inspect( x ) );
}

binance.options( {
  APIKEY: "z5RQZ9n8JcS3HLDQmPpfLQIGGQN6TTs5pCP5CTnn4nYk2ImFcew49v4ZrmP3MGl5",
  APISECRET: "ZqePF1DcLb6Oa0CfcLWH0Tva59y8qBBIqu789JEY27jq0RkOKXpNl9992By1PN9Z",
  useServerTime: true,
  verbose: true, // Add extra output when subscribing to websockets, etc
  log: log => {
    // console.log(log);
  }
} );

binance.prices( "BNBBTC", ( error, ticker ) => {
  assert.ok( typeof( error ) == "object" );
  assert.ok( typeof( ticker ) == "object" );
  assert.ok( error == null );
  assert.ok( ticker != null );
  assert.ok( ticker.hasOwnProperty( "BNBBTC" ) );
  assert.ok( ticker.hasOwnProperty( "ETHBTC" ) == false );
} );

binance.prices( ( error, ticker ) => {
  assert.ok( typeof( error ) == "object" );
  assert.ok( typeof( ticker ) == "object" );
  assert.ok( error == null );
  assert.ok( ticker != null );
  assert.ok( ticker.hasOwnProperty( "BNBBTC" ) );
  assert.ok( Object.keys( ticker ).length >= num_pairs );
} );

binance.balance( ( error, balances ) => {
  assert.ok( error == null );
  assert.ok( balances != null );
  assert.ok( balances );
  assert.ok( balances.hasOwnProperty( "BNB" ) );
  assert.ok( balances.BNB.hasOwnProperty( "available" ) );
  assert.ok( balances.BNB.hasOwnProperty( "onOrder" ) );
  assert.ok( Object.keys( balances ).length >= num_currencies );
} );

binance.bookTickers( "BNBBTC", ( error, ticker ) => {
  assert.ok( error == null );
  assert.ok( ticker != null );
  assert.ok( ticker );

  var members = [ "symbol", "bidPrice", "bidQty", "askPrice", "askQty" ];

  members.forEach( function( value, i ) {
    assert.ok( ticker.hasOwnProperty( value ) );
  } );
} );

binance.bookTickers( ( error, ticker ) => {
  assert.ok( typeof( error ) == "object" );
  assert.ok( typeof( ticker ) == "object" );
  assert.ok( error == null );
  assert.ok( ticker != null );
  assert.ok( Object.keys( ticker ).length >= num_pairs );

  var members = [ "symbol", "bidPrice", "bidQty", "askPrice", "askQty" ];

  ticker.forEach( function( obj, i ) {
    members.forEach( function( member, y ) {
      assert.ok( obj.hasOwnProperty( member ) );
    } );
  } );
} );

binance.depth( "BNBBTC", ( error, depth, symbol ) => {
  assert.ok( error == null );
  assert.ok( depth != null );
  assert.ok( symbol != null );
  assert.ok( typeof( symbol ) === "string" );
  assert.ok( "BNBBTC" === symbol );
  assert.ok( typeof( depth ) === "object" );
  assert.ok( Object.keys( depth ).length == 3 );
  var members = [ "lastUpdateId", "asks", "bids" ];
  members.forEach( function( value, i ) {
    assert.ok( depth.hasOwnProperty( value ) );
  } );
} );

var quantity = 1;
var price = 0.069;
assert.equal( binance.buy( "ETHBTC", quantity, price ), undefined );
assert.equal( binance.sell( "ETHBTC", quantity, price ), undefined );
assert.equal( binance.marketBuy( "BNBBTC", quantity ), undefined );
assert.equal( binance.marketSell( "ETHBTC", quantity ), undefined );

binance.buy( "BNBETH", quantity, price, { type: "LIMIT" }, ( error, response ) => {
  // should be no money in the account
  // debug( error );
  // debug( response );
  assert.ok( typeof( error ) === "object" );
  assert.ok( typeof( response ) === "object" );
  assert.ok( error != null );
  assert.ok( response != null );
  assert.ok( error.body === '{"code":-2010,"msg":"Account has insufficient balance for requested action."}' );
  assert.equal( response.orderId, undefined );
  assert.ok( Object.keys( response ).length == 0 );
} );

var quantity = 1;
binance.marketBuy( "BNBBTC", quantity, ( error, response ) => {
  // should be no money in the account
  // debug( error );
  // debug( response );
  assert.ok( typeof( error ) === "object" );
  assert.ok( typeof( response ) === "object" );
  assert.ok( error != null );
  assert.ok( response != null );
  assert.ok( error.body === '{"code":-2010,"msg":"Account has insufficient balance for requested action."}' );
  assert.equal( response.orderId, undefined );
  assert.ok( Object.keys( response ).length == 0 );
} );

var type = "STOP_LOSS";
var varquantity = 1;
var price = 0.069;
var stopPrice = 0.068;
assert.equal( binance.sell( "ETHBTC", quantity, price, {
  stopPrice: stopPrice,
  type: type
} ), undefined );

var quantity = 1;
var price = 0.069;
assert.equal( binance.sell( "ETHBTC", quantity, price, { icebergQty: 10 } ), undefined );


let orderid = "7610385";
binance.cancel( "ETHBTC", orderid, ( error, response, symbol ) => {
  // should be no money in the account
  // debug( error );
  // debug( response );
  // debug( symbol );
  assert.ok( typeof( error ) === "object" );
  assert.ok( typeof( response ) === "object" );
  assert.ok( error != null );
  assert.ok( response != null );
  assert.ok( error.body === '{"code":-2011,"msg":"UNKNOWN_ORDER"}' );
  assert.equal( response.orderId, undefined );
  assert.ok( Object.keys( response ).length == 0 );
} );

binance.cancelOrders( "XMRBTC", ( error, response, symbol ) => {
  // should be no money in the account
  // debug( error );
  // debug( response );
  // debug( symbol );
  assert.ok( typeof( error ) === "object" );
  assert.ok( typeof( response ) === "object" );
  assert.ok( error == null );
  assert.ok( response != null );
  assert.ok( error.body === '{"code":-2011,"msg":"UNKNOWN_ORDER"}' );
  assert.equal( response.orderId, undefined );
  assert.ok( Object.keys( response ).length == 0 );
} );

binance.openOrders( "ETHBTC", ( error, openOrders, symbol ) => {
  // should be no money in the account
  // debug( error );
  // debug( openOrders );
  // debug( symbol );
  assert.ok( typeof( error ) === "object" );
  assert.ok( typeof( openOrders ) === "object" );
  assert.ok( typeof( symbol ) === "string" );
  assert.ok( symbol === "ETHBTC" );
  assert.ok( error == null );
  assert.ok( openOrders != null );
  assert.ok( symbol != null );
  assert.ok( Object.keys( openOrders ).length == 0 );
} );

binance.openOrders( false, ( error, openOrders ) => {
  // should be no money in the account
  // debug( error );
  // debug( openOrders );
  assert.ok( typeof( error ) === "object" );
  assert.ok( typeof( openOrders ) === "object" );
  assert.ok( error == null );
  assert.ok( openOrders != null );
  assert.ok( Object.keys( openOrders ).length == 0 );
} );


binance.orderStatus( "ETHBTC", orderid, ( error, orderStatus, symbol ) => {
  // should be no money in the account
  // debug( error );
  // debug( orderStatus );
  // debug( symbol );
  assert.ok( typeof( error ) === "object" );
  assert.ok( typeof( orderStatus ) === "object" );
  assert.ok( typeof( symbol ) === "string" );
  assert.ok( symbol === "ETHBTC" );
  assert.ok( error != null );
  assert.ok( orderStatus != null );
  assert.ok( error.body === '{"code":-2013,"msg":"Order does not exist."}' );
  assert.ok( Object.keys( orderStatus ).length == 0 );
} );

binance.trades( "SNMBTC", ( error, trades, symbol ) => {
  // should be no money in the account
  // debug( error );
  // debug( trades );
  // debug( symbol );
  assert.ok( typeof( error ) === "object" );
  assert.ok( typeof( trades ) === "object" );
  assert.ok( typeof( symbol ) === "string" );
  assert.ok( symbol === "SNMBTC" );
  assert.ok( error == null );
  assert.ok( trades != null );
  assert.ok( Object.keys( trades ).length == 0 );
} );

binance.allOrders( "ETHBTC", ( error, orders, symbol ) => {
  // debug( error );
  // debug( orders );
  // debug( symbol );
  assert.ok( typeof( error ) === "object" );
  assert.ok( typeof( orders ) === "object" );
  assert.ok( typeof( symbol ) === "string" );
  assert.ok( symbol === "ETHBTC" );
  assert.ok( error == null );
  assert.ok( orders != null );
  assert.ok( Object.keys( orders ).length == 0 );
} );

binance.prevDay( false, ( error, prevDay ) => {
  // debug( error );
  // debug( prevDay );
  assert.ok( typeof( error ) === "object" );
  assert.ok( typeof( prevDay ) === "object" );
  assert.ok( error == null );
  assert.ok( prevDay != null );
  assert.ok( Object.keys( prevDay ).length >= num_pairs );

  var members = [ "symbol", "priceChange", "priceChangePercent", "weightedAvgPrice", "prevClosePrice",
    "lastPrice", "lastQty", "bidPrice", "bidQty", "askQty", "openPrice", "highPrice", "lowPrice",
    "volume", "quoteVolume", "openTime", "closeTime", "firstId", "lastId", "count" ];

  prevDay.forEach( function( obj, i ) {
    members.forEach( function( key, i ) {
      assert.ok( obj.hasOwnProperty( key ) );
    } );
  } );
} );


binance.prevDay( "BNBBTC", ( error, prevDay, symbol ) => {
  // debug( error );
  // debug( prevDay );
  assert.ok( typeof( error ) === "object" );
  assert.ok( typeof( prevDay ) === "object" );
  assert.ok( typeof( symbol ) === "string" );
  assert.ok( symbol === "BNBBTC" );
  assert.ok( error == null );
  assert.ok( prevDay != null );

  var members = [ "symbol", "priceChange", "priceChangePercent", "weightedAvgPrice", "prevClosePrice",
    "lastPrice", "lastQty", "bidPrice", "bidQty", "askQty", "openPrice", "highPrice", "lowPrice",
    "volume", "quoteVolume", "openTime", "closeTime", "firstId", "lastId", "count" ];

  members.forEach( function( key, i ) {
    assert.ok( prevDay.hasOwnProperty( key ) );
  } );
} );

binance.candlesticks( "BNBBTC", "5m", ( error, ticks, symbol ) => {
  // debug( error );
  // debug( ticks );
  // debug( symbol );
  assert.ok( typeof( error ) === "object" );
  assert.ok( typeof( ticks ) === "object" );
  assert.ok( typeof( symbol ) === "string" );
  assert.ok( symbol === "BNBBTC" );
  assert.ok( error == null );
  assert.ok( ticks != null );

  ticks.forEach( function( tick, i ) {
    assert.ok( tick.length == 12 );
  } );
}, {
  limit: 500,
  endTime: 1514764800000
} );


