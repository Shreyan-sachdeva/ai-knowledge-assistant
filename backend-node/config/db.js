const {Pool} = require('pg')

const pool =new Pool({
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    database: process.env.DB_NAME,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    connectionTimeoutMillis: 5000,
    ssl: process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : false
})

pool.on('error', (err) => {
    console.error('Unexpected error on idle client', err)
})

pool.connect((err) => {
    if(err){
        console.error('Error connection failed',err)
    } else {
        console.log('database connected successfully')
    }
})

module.exports = pool
