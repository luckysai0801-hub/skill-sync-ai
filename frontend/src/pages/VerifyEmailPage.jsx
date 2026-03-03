import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import API from '../services/api'

export default function VerifyEmailPage() {
    const [searchParams] = useSearchParams()
    const navigate = useNavigate()
    const { user } = useAuth()
    const [email, setEmail] = useState('')
    const [verifying, setVerifying] = useState(true)
    const [verified, setVerified] = useState(false)
    const [expired, setExpired] = useState(false)
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)
    const [resendSuccess, setResendSuccess] = useState(false)

    const token = searchParams.get('token')

    useEffect(() => {
        // If user is already logged in and verified, redirect
        if (user && user.email_verified) {
            navigate('/candidate')
            return
        }

        // Auto-verify if token in URL
        if (token) {
            verifyToken()
        } else {
            setVerifying(false)
        }
    }, [token])

    const verifyToken = async () => {
        try {
            const { data } = await API.get(`/auth/verify-email/${token}`)
            if (data.valid) {
                setVerified(true)
                setTimeout(() => navigate('/candidate'), 3000)
            } else {
                setExpired(true)
            }
        } catch (err) {
            setError('Verification failed. Please try again.')
        } finally {
            setVerifying(false)
        }
    }

    const handleResendEmail = async (e) => {
        e.preventDefault()
        if (!email) {
            setError('Please enter your email')
            return
        }

        setLoading(true)
        setError('')

        try {
            await API.post('/auth/resend-verification-email', { email })
            setResendSuccess(true)
            setEmail('')
        } catch (err) {
            setError(err.response?.data?.detail || 'Error sending verification email.')
        } finally {
            setLoading(false)
        }
    }

    if (verifying) {
        return (
            <div className="min-h-screen flex items-center justify-center" style={{ background: '#0f0f1a' }}>
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mb-4"></div>
                    <p className="text-gray-300">Verifying your email...</p>
                </div>
            </div>
        )
    }

    if (verified) {
        return (
            <div className="min-h-screen flex items-center justify-center py-12 px-4" style={{ background: '#0f0f1a' }}>
                <div className="w-full max-w-md p-8 rounded-lg border border-green-500/20 text-center" style={{ background: 'rgba(26,26,46,0.8)' }}>
                    <div className="text-4xl mb-4">✓</div>
                    <h1 className="text-3xl font-bold text-green-400 mb-2">Email Verified!</h1>
                    <p className="text-gray-400 mb-6">Your email has been successfully verified. Redirecting to dashboard...</p>
                    <div className="text-sm text-gray-500">This page will automatically close in a few seconds</div>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen flex items-center justify-center py-12 px-4" style={{ background: '#0f0f1a' }}>
            <div className="w-full max-w-md p-8 rounded-lg border border-indigo-500/20" style={{ background: 'rgba(26,26,46,0.8)' }}>
                <h1 className="text-3xl font-bold text-white mb-2">Verify Email</h1>
                <p className="text-gray-400 mb-8">Confirm your email address to continue</p>

                {expired && (
                    <div className="mb-6 p-4 bg-yellow-500/10 border border-yellow-500/20 rounded text-yellow-400 text-sm">
                        <p>Your verification link has expired.</p>
                        <p>Please request a new one below.</p>
                    </div>
                )}

                {error && (
                    <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded text-red-400 text-sm">
                        {error}
                    </div>
                )}

                {resendSuccess && (
                    <div className="mb-6 p-4 bg-green-500/10 border border-green-500/20 rounded text-green-400 text-sm">
                        <p>Verification email sent! Check your inbox and click the link within it.</p>
                    </div>
                )}

                <form onSubmit={handleResendEmail} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded text-white focus:outline-none focus:border-indigo-500"
                            placeholder="your@email.com"
                            disabled={resendSuccess}
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading || resendSuccess}
                        className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded transition disabled:opacity-50"
                    >
                        {loading ? 'Sending...' : resendSuccess ? 'Email Sent' : 'Resend Verification Email'}
                    </button>
                </form>
            </div>
        </div>
    )
}
