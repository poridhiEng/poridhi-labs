const express = require('express');
const mysql = require('mysql2');
const bodyParser = require('body-parser');

const app = express();
const port = 3002;

const dbConfig = {
  host: 'localhost',
  user: 'my_user',
  password: 'my_password',
  database: 'my_db'
};

// Middleware to parse JSON bodies
app.use(bodyParser.json());

function createConnection() {
  const connection = mysql.createConnection(dbConfig);
  connection.connect(error => {
    if (error) {
      console.error('Error connecting to the database:', error);
      return null;
    }
    console.log('Connected to MySQL database');
  });
  return connection;
}

function createTable() {
  const connection = createConnection();
  if (connection) {
    const createTableQuery = `
      CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE
      )
    `;
    connection.query(createTableQuery, (error, results) => {
      connection.end();
      if (error) {
        console.error('Error creating table:', error);
      } else {
        console.log('Table "users" ensured to exist');
      }
    });
  }
}

// Ensure the table is created when the server starts
createTable();

app.get('/', (req, res) => {
  
  const connection = createConnection();
  if (connection) {
    res.status(200).json({ message: "Hello, from Node App 2! Connected to MySQL database." });
    connection.end();
  } else {
    res.status(500).json({ message: 'Failed to connect to MySQL database' });
  }
});


// GET route to fetch all users
app.get('/users', (req, res) => {
  const connection = createConnection();
  if (connection) {
    connection.query('SELECT * FROM users', (error, results) => {
      connection.end();
      if (error) {
        return res.status(500).json({ message: 'Error fetching users', error });
      }
      res.json(results);
    });
  } else {
    res.status(500).json({ message: 'Failed to connect to MySQL database' });
  }
});

// POST route to add a new user
app.post('/users', (req, res) => {
  const connection = createConnection();
  const { name, email } = req.body;

  if (!name || !email) {
    return res.status(400).json({ message: 'Name and email are required' });
  }

  if (connection) {
    const query = 'INSERT INTO users (name, email) VALUES (?, ?)';
    connection.query(query, [name, email], (error, results) => {
      connection.end();
      if (error) {
        return res.status(500).json({ message: 'Error adding user', error });
      }
      res.status(201).json({ message: 'User added', userId: results.insertId });
    });
  } else {
    res.status(500).json({ message: 'Failed to connect to MySQL database' });
  }
});

app.listen(port, () => {
  console.log(`App running on http://localhost:${port}`);
});
