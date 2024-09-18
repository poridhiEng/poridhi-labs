require('./tracing');
const express = require('express');
const sequelize = require('./config/database');
const redisClient = require('./config/redis');
const User = require('./models/User');
const { trace } = require('@opentelemetry/api');

const app = express();
app.use(express.json());

// Middleware to cache responses
const cache = async (req, res, next) => {
  const { username } = req.params;
  try {
    const data = await redisClient.get(username);
    if (data) {
      return res.json(JSON.parse(data));
    } else {
      next();
    }
  } catch (err) {
    console.error('Redis error:', err);
    next();
  }
};

// Invalidate cache middleware
const invalidateCache = async (req, res, next) => {
  const { username } = req.params;
  if (username) {
    try {
      await redisClient.del(username);
    } catch (err) {
      console.error('Redis error:', err);
    }
  }
  next();
};

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.get('/user', async (req, res) => {
  const span = trace.getTracer('user-service').startSpan('get_all_users');
  try {
    const users = await User.findAll();
    res.json(users);
  } catch (error) {
    span.recordException(error);
    res.status(500).json({ error: error.message });
  } finally {
    span.end();
  }
});

app.get('/user/:username', cache, async (req, res) => {
  const span = trace.getTracer('user-service').startSpan('get_user_by_username');
  span.setAttribute('username', req.params.username);
  try {
    const { username } = req.params;
    const user = await User.findOne({ where: { username } });

    if (user) {
      await redisClient.setEx(username, 3600, JSON.stringify(user));
      res.json(user);
    } else {
      res.status(404).send('User not found');
    }
  } catch (error) {
    span.recordException(error);
    res.status(500).send(error.message);
  } finally {
    span.end();
  }
});

app.post('/user', async (req, res) => {
  const span = trace.getTracer('user-service').startSpan('create_user');
  try {
    const { username, email } = req.body;
    span.setAttributes({ username, email });
    const newUser = await User.create({ username, email });
    res.status(201).json(newUser);
  } catch (error) {
    span.recordException(error);
    res.status(500).send(error.message);
  } finally {
    span.end();
  }
});

app.put('/user/:username', invalidateCache, async (req, res) => {
  const span = trace.getTracer('user-service').startSpan('update_user');
  span.setAttribute('username', req.params.username);
  try {
    const { username } = req.params;
    const { email } = req.body;
    span.setAttribute('new_email', email);
    const user = await User.findOne({ where: { username } });

    if (user) {
      user.email = email;
      await user.save();
      await redisClient.setEx(username, 3600, JSON.stringify(user));
      res.json(user);
    } else {
      res.status(404).send('User not found');
    }
  } catch (error) {
    span.recordException(error);
    res.status(500).send(error.message);
  } finally {
    span.end();
  }
});

app.delete('/user/:username', invalidateCache, async (req, res) => {
  const span = trace.getTracer('user-service').startSpan('delete_user');
  span.setAttribute('username', req.params.username);
  try {
    const { username } = req.params;
    const user = await User.findOne({ where: { username } });

    if (user) {
      await user.destroy();
      await redisClient.del(username);
      res.status(204).send();
    } else {
      res.status(404).send('User not found');
    }
  } catch (error) {
    span.recordException(error);
    res.status(500).send(error.message);
  } finally {
    span.end();
  }
});

const startServer = async () => {
  try {
    await sequelize.sync({ force: true });
    app.listen(5000, () => {
      console.log('Server is running on http://localhost:5000');
    });
  } catch (error) {
    console.error('Unable to connect to the database:', error);
  }
};

startServer();
