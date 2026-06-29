const express = require('express')
const router = express.Router()
const pool = require('../config/db.js')
const bcrypt = require('bcrypt')
const jwt = require('jsonwebtoken')

router.post('/register', async (req, res, next) => {
    try {
        const { username, password } = req.body

        const existing = await pool.query(
            'SELECT * FROM users WHERE username = $1',
            [username]
        )
        if (existing.rows.length > 0) {
            return res.status(400).json({
                success: false,
                message: 'Username already exists'
            })
        }

        const hashedPassword = await bcrypt.hash(password, 10)

        const result = await pool.query(
            'INSERT INTO users (username, password, role) VALUES ($1, $2, $3) RETURNING id, username, role',
            [username, hashedPassword, 'user']
        )

        res.status(201).json({
            success: true,
            message: 'User registered successfully',
            user: result.rows[0]
        })

    } catch (err) {
        next(err)
    }
})

router.post('/login', async (req, res, next) => {
    try {
        const { username, password } = req.body

        const result = await pool.query(
            'SELECT * FROM users WHERE username = $1',
            [username]
        )

        if (result.rows.length === 0) {
            return res.status(401).json({
                success: false,
                message: 'Invalid username or password'
            })
        }

        const user = result.rows[0]

        const validPassword = await bcrypt.compare(password, user.password)

        if (!validPassword) {
            return res.status(401).json({
                success: false,
                message: 'Invalid username or password'
            })
        }

        const token = jwt.sign(
            { id: user.id, username: user.username, role: user.role },
            process.env.JWT_SECRET,
            { expiresIn: '24h' }
        )

        res.status(200).json({
            success: true,
            message: 'Login successful',
            token: token,
            role: user.role
        })

    } catch (err) {
        next(err)
    }
})

module.exports = router