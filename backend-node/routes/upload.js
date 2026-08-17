const express = require('express')
const pool = require('../config/db.js')
const upload = require('../config/multer.js')
const router = express.Router()
const axios = require('axios')
const FormData = require('form-data')

router.post('/upload', upload.single('pdf'), async (req, res, next) => {
    try {
        if(!req.file){
            return res.status(400).json({
                success: false,
                message: 'No file uploaded'
            })
        }

        const result = await pool.query(
            'INSERT INTO documents (filename) VALUES ($1) RETURNING *',
            [req.file.originalname]
        )

        const formData = new FormData()
        formData.append('file', req.file.buffer, req.file.originalname)
        formData.append('documentId', result.rows[0].id)

        try {
            await axios.post(`${process.env.PYTHON_SERVICE_URL}/process`, formData, {
                headers: formData.getHeaders(),
                timeout: 120000,
                maxContentLength: Infinity,
                maxBodyLength: Infinity
            })
        } catch (axiosErr) {
            console.error('AXIOS ERROR DETAILS:')
            console.error('Message:', axiosErr.message)
            console.error('Code:', axiosErr.code)
            console.error('Response status:', axiosErr.response?.status)
            console.error('Response data:', axiosErr.response?.data)
            throw axiosErr
        }

        res.status(200).json({
            success: true,
            message: 'File uploaded successfully',
            document: result.rows[0]
        })

    } catch(err) {
        next(err)
    }
})

router.get('/documents', async (req, res, next) => {
    try {
        const result = await pool.query(
            'SELECT * FROM documents ORDER BY uploaded_at DESC'
        )
        res.status(200).json({
            success: true,
            documents: result.rows
        })
    } catch (err) {
        next(err)
    }
})

router.delete('/documents/:id', async (req, res, next) => {
    try {
        const documentId = req.params.id
        await pool.query(
            `DELETE FROM embeddings 
             WHERE chunk_id IN (
                 SELECT id FROM document_chunks WHERE document_id = $1
             )`,
            [documentId]
        )

        await pool.query(
            'DELETE FROM document_chunks WHERE document_id = $1',
            [documentId]
        )

        const result = await pool.query(
            'DELETE FROM documents WHERE id = $1 RETURNING *',
            [documentId]
        )

        if (result.rows.length === 0) {
            return res.status(404).json({
                success: false,
                message: 'Document not found'
            })
        }

        res.status(200).json({
            success: true,
            message: 'Document deleted successfully',
            deleted: result.rows[0]
        })

    } catch (err) {
        next(err)
    }
})
module.exports = router