import express from 'express';

const PORT = 3001;

let app = express();

app.get('/*', (req, res) => {
	res.send('hello world');
});

app.listen(PORT, () => console.log('Listening on port ' + PORT));