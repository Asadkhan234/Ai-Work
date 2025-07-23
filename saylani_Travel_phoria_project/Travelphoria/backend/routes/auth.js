import express from 'express'
import { deleteUser, getAllUsers, getUserById,  login, signup, updateUser } from '../contollers/authController.js'

const router = express.Router()

router.post('/signup', signup)
router.post('/login', login)
router.put('/update/:id', updateUser)

router.get("/users", getAllUsers)
router.get("/user/:id" , getUserById )
router.delete("/delete/:id", deleteUser)
export default router
