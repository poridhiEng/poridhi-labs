const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
    try {
        res.json({
            message: 'Welcome to NodeJS App. You can now use tools like Postman or curl to test the following endpoints:',
            endpoints: [
                { method: 'POST', route: '/users', description: 'Create a new user.' },
                { method: 'GET', route: '/users', description: 'Get all users.' },
                { method: 'GET', route: '/users/:id', description: 'Get a user by ID.' },
                { method: 'PUT', route: '/users/:id', description: 'Update a user by ID.' },
                { method: 'DELETE', route: '/users/:id', description: 'Delete a user by ID.' }
            ]
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;
