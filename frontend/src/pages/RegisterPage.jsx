import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

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

export default function RegisterPage() {
    const [email, setEmail] = useState('')
    const [name, setName] = useState('')
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [role, setRole] = useState('candidate')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [agreedToTerms, setAgreedToTerms] = useState(false)

    const { register } = useAuth()
    const navigate = useNavigate()

    const strength = getPasswordStrength(password)
    const strengthColors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-lime-500', 'bg-green-500']
    const strengthLabels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong']

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')

        if (password !== confirmPassword) {
            setError('Passwords do not match')
            return
        }

        if (!agreedToTerms) {
            setError('Please accept the terms and conditions')
            return
        }

        setLoading(true)

        try {
            await register(email, name, password, role)
            navigate('/login')
        } catch (err) {
            setError(err.message || 'Registration failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center py-12 px-4" style={{ background: '#0f0f1a' }}>
            <div className="w-full max-w-md p-8 rounded-lg border border-indigo-500/20" style={{ background: 'rgba(26,26,46,0.8)' }}>
                <h1 className="text-3xl font-bold text-white mb-2">Create Account</h1>
                <p className="text-gray-400 mb-8">Join SkillSync AI</p>

                {error && (
                    <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded text-red-400 text-sm">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Full Name</label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            required
                            className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded text-white focus:outline-none focus:border-indigo-500"
                            placeholder="John Doe"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded text-white focus:outline-none focus:border-indigo-500"
                            placeholder="your@email.com"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
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

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">I am a...</label>
                        <div className="space-y-2">
                            <label className="flex items-center">
                                <input
                                    type="radio"
                                    value="candidate"
                                    checked={role === 'candidate'}
                                    onChange={(e) => setRole(e.target.value)}
                                    className="mr-2"
                                />
                                <span className="text-gray-300">Job Seeker (Candidate)</span>
                            </label>
                            <label className="flex items-center">
                                <input
                                    type="radio"
                                    value="employer"
                                    checked={role === 'employer'}
                                    onChange={(e) => setRole(e.target.value)}
                                    className="mr-2"
                                />
                                <span className="text-gray-300">Hiring Manager (Employer)</span>
                            </label>
                        </div>
                    </div>

                    <label className="flex items-center">
                        <input
                            type="checkbox"
                            checked={agreedToTerms}
                            onChange={(e) => setAgreedToTerms(e.target.checked)}
                            className="mr-2"
                        />
                        <span className="text-sm text-gray-400">
                            I agree to the Terms of Service
                        </span>
                    </label>

                    <button
                        type="submit"
                        disabled={loading || !agreedToTerms}
                        className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded transition disabled:opacity-50"
                    >
                        {loading ? 'Creating account...' : 'Create Account'}
                    </button>
                </form>

                <div className="mt-6 text-center">
                    <p className="text-gray-400">
                        Already have an account?{' '}
                        <Link to="/login" className="text-indigo-400 hover:text-indigo-300">
                            Sign in
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    )
}
