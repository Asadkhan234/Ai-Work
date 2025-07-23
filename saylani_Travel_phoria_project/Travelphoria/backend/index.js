import express from 'express'
import dotenv from 'dotenv'
import router from './routes/auth.js'
import connectDB from './config/db.js'

dotenv.config()
connectDB()

const app = express()

app.use(express.json())

// Mount the main router
app.use('/', router)



const PORT = process.env.PORT || 5000
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`)
})
