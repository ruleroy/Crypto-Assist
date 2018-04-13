import express from 'express';
var PythonShell = require('python-shell');

const PORT = 3001;

let app = express();


app.use(function(req, res, next) {
	res.header("Access-Control-Allow-Origin", "*");
	res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
	next();
});

app.get('/api/get-data', function(request, response){
	var pair = request.query.pair;

	var options = {
		mode: 'text',
		pythonOptions: ['-u'], 
		scriptPath: './scripts',
		args: ['-j', 'BTCUSDT']
	};

	console.log('get chart data for ' + pair);

	PythonShell.run('bot.py', options, function (err, results) {
		if (err) {
			console.log(err);
			return response.status(400).send('fail');
		}
		//console.log('results: %j', results[1]);

		var items = JSON.parse(results[1].slice(0, -1));

		//console.log(items);
		var min = Math.min(items.close);
		var max = Math.max(items.close);
		
		
		return response.status(200).json({
			labels: items.date,
			series: [items.close],
			lowest: min,
			highest: max
		});
		
	});

});

app.get('/api/get-acc', function(request, response){
	var pair = request.query.pair;

	var options = {
		mode: 'text',
		pythonOptions: ['-u'], 
		scriptPath: './scripts',
		args: ['-w']
	};

	console.log('get acc data');

	PythonShell.run('bot.py', options, function (err, results) {
		if (err) {
			console.log(err);
			return response.status(400).send('fail');
		}
		//console.log('results: %j', results[3]);
		var items = JSON.parse(results[3].slice(0, -1));
		var total_btc_val = results[4];
		var total_usd_val = results[5];
		var btc_price = results[6];

		console.log(total_btc_val);
		console.log(total_usd_val);
		
		return response.status(200).json({
			btc_bal: items.BTC,
			total_btc_val: total_btc_val,
			total_usd_val: total_usd_val,
			btc_price: btc_price
		});
		
	});

});


app.listen(PORT, () => console.log('Listening on port ' + PORT));