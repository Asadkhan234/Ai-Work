import bcrypt from 'bcryptjs'
import jwt from 'jsonwebtoken'
import User from '../models/user.js'

// Signup Controller
export const signup = async (req, res) => {
  const { name, email, password } = req.body

  try {
    const existingUser = await User.findOne({ email })
    if (existingUser) return res.status(400).json({ message: 'User already exists' })

    const hashedPassword = await bcrypt.hash(password, 10)

    const user = await User.create({ name, email, password: hashedPassword })
    if (!user) return res.status(500).json({ message: 'User creation failed' })

    const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: '7d' })

    res.status(201).json({ user, token })
  } catch (error) {
    res.status(500).json({ message: 'Signup failed', error: error.message })
  }
}

// Login Controller
export const login = async (req, res) => {
  const { email, password } = req.body

  try {
    const user = await User.findOne({ email })
    if (!user) return res.status(404).json({ message: 'User not found' })

    const isMatch = await bcrypt.compare(password, user.password)
    if (!isMatch) return res.status(400).json({ message: 'Invalid credentials' })

    const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: '7d' })

    res.status(200).json({ user, token })
  } catch (error) {
    res.status(500).json({ message: 'Login failed', error: error.message })
  }
}
 
// Get all users
export const getAllUsers = async (req, res) => {
  try {
    const users = await User.find().select("-password") // password hide karna zaroori hai
    res.status(200).json(users)
  } catch (error) {
    res.status(500).json({ message: 'Fetching users failed', error: error.message })
  }
}

// Get user by ID
export const getUserById = async (req, res) => {
  const { id } = req.params
  try {
    const user = await User.findById(id).select("-password")
    if (!user) return res.status(404).json({ message: 'User not found' })
    res.status(200).json(user)
  } catch (error) {
    res.status(500).json({ message: 'Fetching user failed', error: error.message })
  }
}

export const updateUser = async (req, res) => {
  const { id } = req.params
  const { name, email, password } = req.body

  try {
    const user = await User.findById(id)
    if (!user) return res.status(404).json({ message: 'User not found' })

    if (name) user.name = name
    if (email) user.email = email

    // Optional: agar password change karna ho toh
    if (password) {
      const bcrypt = await import('bcryptjs')
      const hashedPassword = await bcrypt.hash(password, 10)
      user.password = hashedPassword
    }

    const updatedUser = await user.save()
    res.status(200).json({
      message: 'Profile updated',
      user: {
        id: updatedUser._id,
        name: updatedUser.name,
        email: updatedUser.email,
      }
    })
  } catch (error) {
    res.status(500).json({ message: 'Update failed', error: error.message })
  }
}

// Get user by ID (custom route style: /user/id/:id)
export const deleteUser = async (req, res) => {
  const { id } = req.params
  try {
    const user = await User.findByIdAndDelete(id)
    if (!user) return res.status(404).json({ message: 'User not found' })
    res.status(200).json({ message: 'User deleted successfully' })
  } catch (error) {
    res.status(500).json({ message: 'Deletion failed', error: error.message })
  }
}
// Middleware to protect routes