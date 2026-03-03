import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate, Link } from 'react-router-dom'

function getPasswordStrength(password) {
    let score = 0
    let feedback = []

    if (password.length >= 8) score += 1
    else feedback.push('At least 8 characters')

    if (/[A-Z]/.test(password)) score += 1
    else feedback.push('Add uppercase')

    if (/[a-z]/.test(password)) score += 1
    else feedback.push('Add lowercase')

    if (/\d/.test(password)) score += 1
    else feedback.push('Add number')

    if (/[!@#$%^&*]/.test(password)) score += 1
    else feedback.push('Add special char')

    return { score, feedback }
}

export default function ResetPasswordPage() {
    const [searchParams] = useSearchParams()
    const navigate = useNavigate()
    const token = searchParams.get('token')

    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [validating, setValidating] = useState(true)
    const [tokenValid, setTokenValid] = useState(false)
    const [success, setSuccess] = useState(false)

    const strength = getPasswordStrength(password)
    const strengthColors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-lime-500', 'bg-green-500']
    const strengthLabels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong']

    useEffect(() => {
        if (!token) {
            setError('No reset token provided')
            setValidating(false)
            return
        }

        // Validate token
        fetch(`http://localhost:8000/auth/validate-reset-token/${token}`, {
            method: 'GET',
            credentials: 'include',
        })
            .then((res) => res.json())
            .then((data) => {
                setTokenValid(data.valid)
                if (!data.valid) {
                    setError('Reset link has expired or is invalid')
                }
            })
            .catch(() => {
                setError('Failed to validate reset link')
            })
            .finally(() => {
                setValidating(false)
            })
    }, [token])

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')

        if (password !== confirmPassword) {
            setError('Passwords do not match')
            return
        }

        if (strength.score < 3) {
            setError('Password is too weak. Please meet all requirements.')
            return
        }

        setLoading(true)

        try {
            const response = await fetch('http://localhost:8000/auth/reset-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ token, password }),
            })

            if (response.ok) {
                setSuccess(true)
                setTimeout(() => navigate('/login'), 2000)
            } else {
                const data = await response.json()
                setError(data.detail || 'Failed to reset password')
            }
        } catch (err) {
            setError('Error resetting password. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    if (validating) {
        return (
            <div className="min-h-screen flex items-center justify-center" style={{ background: '#0f0f1a' }}>
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mb-4"></div>
                    <p className="text-gray-300">Validating reset link...</p>
                </div>
            </div>
        )
    }

    if (!tokenValid) {
        return (
            <div className="min-h-screen flex items-center justify-center py-12 px-4" style={{ background: '#0f0f1a' }}>
                <div className="w-full max-w-md p-8 rounded-lg border border-red-500/20" style={{ background: 'rgba(26,26,46,0.8)' }}>
                    <h1 className="text-3xl font-bold text-white mb-2">Reset Link Expired</h1>
                    <p className="text-gray-400 mb-8">Your reset link has expired or is invalid.</p>

                    <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded text-yellow-400 text-sm mb-6">
                        Reset links expire after 1 hour. Please request a new one.
                    </div>

                    <Link
                        to="/forgot-password"
                        className="block w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded transition text-center"
                    >
                        Request New Reset Link
                    </Link>
                </div>
            </div>
        )
    }

    if (success) {
        return (
            <div className="min-h-screen flex items-center justify-center py-12 px-4" style={{ background: '#0f0f1a' }}>
                <div className="w-full max-w-md p-8 rounded-lg border border-green-500/20 text-center" style={{ background: 'rgba(26,26,46,0.8)' }}>
                    <div className="text-4xl mb-4">✓</div>
                    <h1 className="text-3xl font-bold text-green-400 mb-2">Password Reset!</h1>
                    <p className="text-gray-400 mb-6">Your password has been successfully reset. Redirecting to login...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen flex items-center justify-center py-12 px-4" style={{ background: '#0f0f1a' }}>
            <div className="w-full max-w-md p-8 rounded-lg border border-indigo-500/20" style={{ background: 'rgba(26,26,46,0.8)' }}>
                <h1 className="text-3xl font-bold text-white mb-2">Reset Password</h1>
                <p className="text-gray-400 mb-8">Enter your new password</p>

                {error && (
                    <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded text-red-400 text-sm">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">New Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded text-white focus:outline-none focus:border-indigo-500"
                            placeholder="••••••••"
                        />
                        {password && (
                            <>
                                <div className="mt-2 flex gap-1">
                                    {[0, 1, 2, 3, 4].map((i) => (
                                        <div
                                            key={i}
                                            className={`h-1 flex-1 rounded ${i < strength.score ? strengthColors[strength.score - 1] : 'bg-gray-700'}`}
                                        />
                                    ))}
                                </div>
                                <p className="mt-1 text-xs text-gray-400">
                                    {strengthLabels[Math.max(0, strength.score - 1)]}
                                </p>
                                {strength.feedback.length > 0 && (
                                    <p className="mt-1 text-xs text-gray-400">
                                        {strength.feedback.join(', ')}
                                    </p>
                                )}
                            </>
                        )}
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Confirm Password</label>
                        <input
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                            className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded text-white focus:outline-none focus:border-indigo-500"
                            placeholder="••••••••"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading || strength.score < 3}
                        className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded transition disabled:opacity-50"
                    >
                        {loading ? 'Resetting...' : 'Reset Password'}
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
