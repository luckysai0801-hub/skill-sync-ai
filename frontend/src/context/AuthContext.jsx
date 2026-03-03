import React, { createContext, useContext, useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import API from '../services/api'

const AuthContext = createContext(null)

// ─── Token helpers ────────────────────────────────────────────────────────────
const TOKEN_KEY = 'skillsync_token'

function saveToken(token) {
    localStorage.setItem(TOKEN_KEY, token)
    API.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

function clearToken() {
    localStorage.removeItem(TOKEN_KEY)
    delete API.defaults.headers.common['Authorization']
}

function loadToken() {
    const token = localStorage.getItem(TOKEN_KEY)
    if (token) {
        API.defaults.headers.common['Authorization'] = `Bearer ${token}`
    }
    return token
}

// ─── Provider ─────────────────────────────────────────────────────────────────
export function AuthProvider({ children }) {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const token = loadToken()
        if (!token) {
            setLoading(false)
            return
        }
        // Validate the stored token
        API.get('/auth/me')
            .then(({ data }) => setUser(data))
            .catch(() => {
                clearToken()
                setUser(null)
            })
            .finally(() => setLoading(false))
    }, [])

    const register = async (email, name, password, role) => {
        try {
            const { data } = await API.post('/auth/register', { email, name, password, role })
            toast.success('Account created! You can now sign in.')
            return data
        } catch (error) {
            const msg = error.response?.data?.detail || 'Registration failed'
            toast.error(msg)
            throw new Error(msg)
        }
    }

    const login = async (email, password) => {
        try {
            const { data } = await API.post('/auth/login', { email, password })
            // Store token and set Authorization header for all future requests
            saveToken(data.access_token)
            setUser(data.user)
            toast.success('Logged in successfully!')
            return data.user
        } catch (error) {
            const msg = error.response?.data?.detail || 'Login failed'
            toast.error(msg)
            throw new Error(msg)
        }
    }

    const logout = async () => {
        clearToken()
        setUser(null)
        toast.success('Logged out')
        // Best-effort server-side logout
        try { await API.post('/auth/logout') } catch { /* ignore */ }
    }

    const verifyEmail = async (token) => {
        try {
            const { data } = await API.get(`/auth/verify-email/${token}`)
            if (data.valid) {
                setUser(prev => prev ? { ...prev, email_verified: true } : prev)
                toast.success('Email verified successfully!')
                return true
            }
            toast.error(data.message || 'Verification failed')
            return false
        } catch {
            toast.error('Verification error')
            return false
        }
    }

    return (
        <AuthContext.Provider value={{ user, loading, register, login, logout, verifyEmail }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (!context) throw new Error('useAuth must be used within AuthProvider')
    return context
}
