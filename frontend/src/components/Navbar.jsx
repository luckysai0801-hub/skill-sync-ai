/**
 * components/Navbar.jsx – Top navigation bar with user profile and logout.
 */
import { useState } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
    const navigate = useNavigate()
    const location = useLocation()
    const { user, logout } = useAuth()
    const [showDropdown, setShowDropdown] = useState(false)

    const handleLogout = async () => {
        await logout()
        navigate('/login')
    }

    return (
        <>
            <nav className="fixed top-0 left-0 right-0 z-50 border-b border-gray-800"
                style={{ background: 'rgba(0, 0, 0, 0.95)', backdropFilter: 'blur(20px)' }}>
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    {/* Logo */}
                    <button
                        onClick={() => navigate('/')}
                        className="flex items-center gap-3 group"
                    >
                        <div className="w-9 h-9 rounded-lg flex items-center justify-center bg-white">
                            <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5 text-black">
                                <path d="M12 2L2 7l10 5 10-5-10-5z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
                                <path d="M2 17l10 5 10-5" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
                                <path d="M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
                            </svg>
                        </div>
                        <span className="font-bold text-lg text-white">SkillSync AI</span>
                    </button>

                    {/* Center Nav Links */}
                    {user && (
                        <div className="hidden md:flex items-center gap-1">
                            {user.role === 'candidate' ? (
                                <>
                                    <NavLink to="/candidate" label="Dashboard" current={location.pathname} />
                                    <NavLink to="/candidate/jobs" label="Browse Jobs" current={location.pathname} />
                                    <NavLink to="/candidate/resume" label="Resume Score" current={location.pathname} />
                                </>
                            ) : (
                                <>
                                    <NavLink to="/employer" label="Dashboard" current={location.pathname} />
                                    <NavLink to="/employer/create-job" label="Post Job" current={location.pathname} />
                                    <NavLink to="/employer/analytics" label="Analytics" current={location.pathname} />
                                </>
                            )}
                        </div>
                    )}

                    {/* Right Side: Auth Section */}
                    <div className="flex items-center gap-4">
                        {user ? (
                            <div className="relative">
                                <button
                                    onClick={() => setShowDropdown(!showDropdown)}
                                    className="flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-white/10 transition"
                                >
                                    <div className="w-8 h-8 rounded-full flex items-center justify-center bg-indigo-600">
                                        <span className="text-white text-sm font-bold">{user.name[0]}</span>
                                    </div>
                                    <span className="text-gray-300 text-sm">{user.email}</span>
                                </button>

                                {showDropdown && (
                                    <div className="absolute right-0 mt-2 w-48 rounded-lg shadow-lg border border-gray-700"
                                        style={{ background: 'rgba(26,26,46,0.95)' }}>
                                        <div className="p-4 border-b border-gray-700">
                                            <p className="text-gray-400 text-xs">Logged in as</p>
                                            <p className="text-white text-sm font-semibold">{user.name}</p>
                                        </div>
                                        <button
                                            onClick={handleLogout}
                                            className="w-full text-left px-4 py-2 text-red-400 hover:bg-red-500/10 transition text-sm"
                                        >
                                            Logout
                                        </button>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="flex items-center gap-2">
                                <Link to="/login" className="px-4 py-2 text-gray-300 hover:text-white text-sm font-medium">
                                    Sign in
                                </Link>
                                <Link to="/register" className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-semibold">
                                    Register
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </nav>


        </>
    )
}

function NavLink({ to, label, current }) {
    const isActive = current === to || current.startsWith(to + '/')
    return (
        <Link
            to={to}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${isActive
                ? 'text-white bg-white/15'
                : 'text-gray-400 hover:text-white hover:bg-white/8'
                }`}
        >
            {label}
        </Link>
    )
}

