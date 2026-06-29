const express = require('express')
const pool = require('../config/db.js')
const upload = require('../config/multer.js')
const router = express.Router()
const axios = require('axios')
const { protect, adminOnly } = require('../middleware/authMiddleware.js')

router.post('/upload', protect, adminOnly, upload.single('pdf'), async (req, res, next) => {
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

        await axios.post(`${process.env.PYTHON_SERVICE_URL}/process`,{
            filePath: require('path').resolve(req.file.path),
            documentId: result.rows[0].id
        })
        res.status(200).json({
            success: true,
            message: 'File uploaded succesfully',
            document: result.rows[0]
        })
    }catch(err){        
        next(err)
    }
})
router.get('/documents', protect, adminOnly, async (req, res, next) => {
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
//:id id url paramter user send id here
router.delete('/documents/:id', protect, adminOnly, async (req, res, next) => {
    try {
        //used for parameters
        const documentId = req.params.id
        //IN is used with WHERE to check in a column for the items mentioned in list
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