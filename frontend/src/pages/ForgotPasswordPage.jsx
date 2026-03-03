import { useState } from 'react'
import { Link } from 'react-router-dom'

export default function ForgotPasswordPage() {
    const [email, setEmail] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState(false)

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')

        if (!email) {
            setError('Email is required')
            return
        }

        setLoading(true)

        try {
            const response = await fetch('http://localhost:8000/auth/forgot-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ email }),
            })

            if (response.ok) {
                setSuccess(true)
                setEmail('')
            } else {
                // Always show generic success message for security
                setSuccess(true)
                setEmail('')
            }
        } catch (err) {
            setError('Error processing request. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center py-12 px-4" style={{ background: '#0f0f1a' }}>
            <div className="w-full max-w-md p-8 rounded-lg border border-indigo-500/20" style={{ background: 'rgba(26,26,46,0.8)' }}>
                <h1 className="text-3xl font-bold text-white mb-2">Reset Password</h1>
                <p className="text-gray-400 mb-8">Enter your email to receive a password reset link</p>

                {error && (
                    <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded text-red-400 text-sm">
                        {error}
                    </div>
                )}

                {success ? (
                    <div className="p-4 bg-green-500/10 border border-green-500/20 rounded text-green-400 text-sm mb-6">
                        <p>If that email exists in our system, you will receive a password reset link shortly.</p>
                        <p className="mt-2">Check your inbox and click the link to reset your password. Links expire in 1 hour.</p>
                    </div>
                ) : null}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded text-white focus:outline-none focus:border-indigo-500"
                            placeholder="your@email.com"
                            disabled={success}
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading || success}
                        className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded transition disabled:opacity-50"
                    >
                        {loading ? 'Sending...' : 'Send Reset Link'}
                    </button>
                </form>

                <div className="mt-6 text-center">
                    <p className="text-gray-400">
                        Remember your password?{' '}
                        <Link to="/login" className="text-indigo-400 hover:text-indigo-300">
                            Sign in
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    )
}
