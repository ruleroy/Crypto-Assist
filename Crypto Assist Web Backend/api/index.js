const express = require('express');
var PythonShell = require('python-shell');

const PORT = 3001;

let app = express();


app.use(function(req, res, next) {
	res.header("Access-Control-Allow-Origin", "*");
	res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
	next();
});

app.get('/api/get-charts', function(request, response){
	var pair = request.query.pair;

	var options = {
		mode: 'text',
		pythonOptions: ['-u'], 
		scriptPath: './scripts',
		args: ['-k', pair]
	};

	console.log('generating heatmap ' + pair);

	PythonShell.run('bot.py', options, function (err, results) {
		if (err) {
			console.log(err);
			return response.status(400).send('fail');
		}
		console.log(results)
		return response.status(200).json({
			success: true
		});
		
	});

});

app.get('/api/get-data', function(request, response){
	var pair = request.query.pair;

	var options = {
		mode: 'text',
		pythonOptions: ['-u'], 
		scriptPath: './scripts',
		args: ['-j', pair]
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

app.get('/api/get-analyze-coin', function(request, response){
	var pair = request.query.pair;

	var options = {
		mode: 'text',
		pythonOptions: ['-u'], 
		scriptPath: './scripts',
		args: ['-d', pair]
	};

	console.log('analyzing ' + pair);

	PythonShell.run('bot.py', options, function (err, results) {
		if (err) {
			console.log(err);
			return response.status(400).send('fail');
		}
		//console.log('results: %j', results[1]);

		var items = JSON.parse(results[2].slice(0, -1));
		var acc = JSON.parse(results[1].slice(0, -1));

		console.log(items);

		var data = []
		var i;
		for (i = 0; i < items.length; i++){
			var d = {
				time: items[i].time,
				price: items[i].price,
				linearY: items[i].linearY,
				ptime: items[i].ptime,
				prediction: items[i].prediction,
				rtime: items[i].rtime,
				rprice: items[i].rprice
			};
			data.push(d);
		}
		var f = {
				accuracy: acc
			};
		data.push(f);
		console.log(f);
		return response.status(200).json(data);
	});

});

app.get('/api/get-data2', function(request, response){
	var pair = request.query.pair;

	var options = {
		mode: 'text',
		pythonOptions: ['-u'], 
		scriptPath: './scripts',
		args: ['-j', pair]
	};

	console.log('get chart data2 for ' + pair);

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


		var data = []
		var i;
		for (i = 0; i < items.close.length; i++){
			var d = {
				date: items.date[i],
				price: items.close[i]
			};
			data.push(d);
		}

		console.log(data);
		return response.status(200).json(data);
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