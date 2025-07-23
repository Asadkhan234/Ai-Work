import express from 'express'
import authRoutes from './auth.js'
import protectedRoutes from './protected.js'
import connectDB from '../config/db.js'


const router = express.Router()

router.get('/', (req, res) => {
  res.json({ message: 'API is running ' })
})

router.use('/auth', authRoutes)
router.use('/user',protectedRoutes)
export default router
