require('dotenv').config();
const express = require('express');
const app = express();
const port = process.env.PORT;


app.get('/', (req, res) => {
  res.status(200).send(`Hello, from Node App on PORT: ${port}!`);
});

app.get('/users', (req, res) => {
    res.status(200).send(`Congratulations! You have reached the users endpoint!`);
});

app.listen(port, () => {
  console.log(`App running on http://localhost:${port}`);
});
