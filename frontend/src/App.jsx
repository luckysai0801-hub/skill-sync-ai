/**
 * App.jsx – Root application component with routing and authentication.
 *
 * Routes:
 *   /                   → LandingPage (public)
 *   /login              → LoginPage (public)
 *   /register           → RegisterPage (public)
 *   /verify-email       → VerifyEmailPage (public)
 *   /forgot-password    → ForgotPasswordPage (public)
 *   /reset-password     → ResetPasswordPage (public)
 *   /candidate/*        → CandidateDashboard (protected, requires email verification)
 *   /employer/*         → EmployerDashboard (protected, requires email verification)
 */
import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'

import { AuthProvider } from './context/AuthContext'
import { useAuth } from './context/AuthContext'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'

import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import VerifyEmailPage from './pages/VerifyEmailPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import CandidateDashboard from './pages/CandidateDashboard'
import EmployerDashboard from './pages/EmployerDashboard'
import AnalyticsDashboard from './pages/AnalyticsDashboard'

function AppRoutes() {
    const { loading } = useAuth()

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center" style={{ background: '#0f0f1a' }}>
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mb-4"></div>
                    <p className="text-gray-300">Loading...</p>
                </div>
            </div>
        )
    }

    return (
        <>
            <Navbar />
            <Routes>
                {/* Public Routes */}
                <Route path="/" element={<LandingPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/verify-email" element={<VerifyEmailPage />} />
                <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                <Route path="/reset-password" element={<ResetPasswordPage />} />

                {/* Protected Candidate Routes */}
                <Route
                    path="/candidate"
                    element={
                        <ProtectedRoute requiredRole="candidate" requireVerified={false}>
                            <CandidateDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/candidate/jobs"
                    element={
                        <ProtectedRoute requiredRole="candidate" requireVerified={false}>
                            <CandidateDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/candidate/resume"
                    element={
                        <ProtectedRoute requiredRole="candidate" requireVerified={false}>
                            <CandidateDashboard />
                        </ProtectedRoute>
                    }
                />

                {/* Protected Employer Routes */}
                <Route
                    path="/employer"
                    element={
                        <ProtectedRoute requiredRole="employer" requireVerified={false}>
                            <EmployerDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/employer/create-job"
                    element={
                        <ProtectedRoute requiredRole="employer" requireVerified={false}>
                            <EmployerDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/employer/analytics"
                    element={
                        <ProtectedRoute requiredRole="employer" requireVerified={false}>
                            <AnalyticsDashboard />
                        </ProtectedRoute>
                    }
                />

                {/* Fallback */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </>
    )
}

export default function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <div className="min-h-screen" style={{ background: '#0f0f1a' }}>
                    {/* Global toast notifications */}
                    <Toaster
                        position="top-right"
                        toastOptions={{
                            style: {
                                background: 'rgba(26,26,46,0.95)',
                                border: '1px solid rgba(99,102,241,0.3)',
                                color: '#e2e8f0',
                                borderRadius: '12px',
                                backdropFilter: 'blur(20px)',
                            },
                            success: { iconTheme: { primary: '#10b981', secondary: '#0f0f1a' } },
                            error: { iconTheme: { primary: '#ef4444', secondary: '#0f0f1a' } },
                        }}
                    />

                    <AppRoutes />
                </div>
            </BrowserRouter>
        </AuthProvider>
    )
}
