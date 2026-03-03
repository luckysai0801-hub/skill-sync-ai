/**
 * pages/LandingPage.jsx – Hero landing page for SkillSync AI.
 */
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const features = [
    { icon: '🧠', title: 'Semantic AI Matching', desc: 'All-MiniLM-L6-v2 embeddings capture meaning beyond keywords.' },
    { icon: '🎯', title: 'Explainable Scores', desc: 'Full breakdown: semantics, skills, experience, location, salary.' },
    { icon: '🔍', title: 'Skill Gap Analysis', desc: 'See exactly what skills you need and simulate score improvement.' },
    { icon: '📄', title: 'Resume Intelligence', desc: 'AI-powered resume scoring with actionable improvement tips.' },
    { icon: '📊', title: 'Recruiter Analytics', desc: 'Dashboard with charts, rankings, and candidate comparisons.' },
    { icon: '🎲', title: 'Interview Probability', desc: 'AI-estimated likelihood of landing an interview call.' },
]

export default function LandingPage() {
    const navigate = useNavigate()
    const [hoveredFeature, setHoveredFeature] = useState(null)

    const goCandidate = () => { navigate('/login') }
    const goEmployer = () => { navigate('/login') }

    return (
        <>
            {/* Hero Section */}
            <div className="min-h-screen bg-black text-white flex items-center relative overflow-hidden">
                {/* Subtle Grid Background */}
                <div className="absolute inset-0 opacity-5" style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

                <div className="container mx-auto px-6 flex flex-col md:flex-row items-center relative z-10">
                    {/* Left Column */}
                    <div className="w-full md:w-1/2 mb-12 md:mb-0">
                        <div className="inline-block mb-6 px-4 py-2 rounded-full border border-gray-700 bg-gray-900 text-gray-300 text-sm font-medium">
                            ✨ Advanced AI Matching
                        </div>

                        <h1 className="text-6xl md:text-7xl font-black leading-tight mb-6 tracking-tight">
                            <span className="text-white">SkillSync</span>
                            <br />
                            <span className="text-gray-400">AI</span>
                        </h1>

                        <p className="mt-6 text-xl text-gray-400 max-w-2xl leading-relaxed font-light">
                            Intelligent job matching through semantic AI. Discover opportunities that truly align with your skills and experience.
                        </p>

                        <div className="mt-12 flex flex-col sm:flex-row gap-4">
                            <button
                                onClick={goEmployer}
                                className="group relative px-8 py-4 rounded-lg font-semibold text-black bg-white transition-all duration-300 hover:shadow-2xl transform hover:-translate-y-1 overflow-hidden"
                            >
                                <span className="relative z-10 flex items-center justify-center gap-2">
                                    Recruiter Portal
                                    <span className="inline-block transition-transform group-hover:translate-x-1">→</span>
                                </span>
                            </button>

                            <button
                                onClick={goCandidate}
                                className="group px-8 py-4 rounded-lg font-semibold text-black bg-white transition-all duration-300 hover:shadow-2xl transform hover:-translate-y-1"
                            >
                                <span className="flex items-center justify-center gap-2">
                                    Candidate View
                                    <span className="inline-block transition-transform group-hover:translate-x-1">→</span>
                                </span>
                            </button>
                        </div>
                    </div>

                    {/* Right Column */}
                    <div className="w-full md:w-1/2 flex justify-center md:justify-end">
                        <div className="relative w-full max-w-md">
                            <div className="relative h-96 rounded-2xl border border-gray-800 flex items-center justify-center backdrop-blur-sm bg-gray-950 overflow-hidden">
                                {/* Minimalist AI Illustration */}
                                <svg className="w-full h-full" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
                                    {/* Background */}
                                    <rect width="400" height="400" fill="none" />

                                    {/* Central Neural Network Circle */}
                                    <circle cx="200" cy="200" r="120" fill="none" stroke="#ffffff" strokeWidth="1" opacity="0.1" />
                                    <circle cx="200" cy="200" r="100" fill="none" stroke="#ffffff" strokeWidth="1" opacity="0.15" />
                                    <circle cx="200" cy="200" r="80" fill="none" stroke="#ffffff" strokeWidth="1" opacity="0.2" />

                                    {/* Center Node */}
                                    <circle cx="200" cy="200" r="12" fill="#ffffff" />
                                    <circle cx="200" cy="200" r="8" fill="none" stroke="#ffffff" strokeWidth="2" />

                                    {/* Top Nodes */}
                                    <circle cx="200" cy="80" r="8" fill="#ffffff" opacity="0.7" />
                                    <line x1="200" y1="200" x2="200" y2="88" stroke="#ffffff" strokeWidth="1.5" opacity="0.4" />

                                    <circle cx="140" cy="100" r="7" fill="#ffffff" opacity="0.6" />
                                    <line x1="200" y1="200" x2="140" y2="107" stroke="#ffffff" strokeWidth="1.5" opacity="0.3" />

                                    <circle cx="260" cy="100" r="7" fill="#ffffff" opacity="0.6" />
                                    <line x1="200" y1="200" x2="260" y2="107" stroke="#ffffff" strokeWidth="1.5" opacity="0.3" />

                                    {/* Bottom Nodes */}
                                    <circle cx="200" cy="320" r="8" fill="#ffffff" opacity="0.7" />
                                    <line x1="200" y1="200" x2="200" y2="312" stroke="#ffffff" strokeWidth="1.5" opacity="0.4" />

                                    <circle cx="140" cy="300" r="7" fill="#ffffff" opacity="0.6" />
                                    <line x1="200" y1="200" x2="140" y2="293" stroke="#ffffff" strokeWidth="1.5" opacity="0.3" />

                                    <circle cx="260" cy="300" r="7" fill="#ffffff" opacity="0.6" />
                                    <line x1="200" y1="200" x2="260" y2="293" stroke="#ffffff" strokeWidth="1.5" opacity="0.3" />

                                    {/* Side Nodes */}
                                    <circle cx="80" cy="200" r="8" fill="#ffffff" opacity="0.7" />
                                    <line x1="200" y1="200" x2="88" y2="200" stroke="#ffffff" strokeWidth="1.5" opacity="0.4" />

                                    <circle cx="320" cy="200" r="8" fill="#ffffff" opacity="0.7" />
                                    <line x1="200" y1="200" x2="312" y2="200" stroke="#ffffff" strokeWidth="1.5" opacity="0.4" />

                                    {/* Diagonal Nodes */}
                                    <circle cx="120" cy="120" r="6" fill="#ffffff" opacity="0.5" />
                                    <line x1="200" y1="200" x2="120" y2="120" stroke="#ffffff" strokeWidth="1" opacity="0.2" />

                                    <circle cx="280" cy="120" r="6" fill="#ffffff" opacity="0.5" />
                                    <line x1="200" y1="200" x2="280" y2="120" stroke="#ffffff" strokeWidth="1" opacity="0.2" />

                                    <circle cx="120" cy="280" r="6" fill="#ffffff" opacity="0.5" />
                                    <line x1="200" y1="200" x2="120" y2="280" stroke="#ffffff" strokeWidth="1" opacity="0.2" />

                                    <circle cx="280" cy="280" r="6" fill="#ffffff" opacity="0.5" />
                                    <line x1="200" y1="200" x2="280" y2="280" stroke="#ffffff" strokeWidth="1" opacity="0.2" />

                                    {/* Text Label */}
                                    <text x="200" y="370" textAnchor="middle" fill="#999999" fontSize="12" fontFamily="Inter, sans-serif">
                                        Semantic Matching Engine
                                    </text>
                                </svg>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Features Section */}
            <section className="py-24 bg-black border-t border-gray-900">
                <div className="container mx-auto px-6">
                    <div className="mb-16">
                        <h2 className="text-4xl md:text-5xl font-black text-white mb-4 tracking-tight">
                            Everything You Need
                        </h2>
                        <p className="text-gray-500 text-lg max-w-2xl font-light">
                            Comprehensive tools for intelligent job matching and career growth
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {features.map(({ icon, title, desc }, idx) => (
                            <div
                                key={title}
                                onClick={() => navigate('/login')}
                                onMouseEnter={() => setHoveredFeature(idx)}
                                onMouseLeave={() => setHoveredFeature(null)}
                                className="group relative p-8 rounded-xl border transition-all duration-300 cursor-pointer transform hover:-translate-y-1"
                                style={{
                                    background: hoveredFeature === idx ? '#111111' : '#000000',
                                    borderColor: hoveredFeature === idx ? '#ffffff' : '#333333',
                                    boxShadow: hoveredFeature === idx ? '0 20px 40px rgba(0,0,0,0.8)' : 'none',
                                }}
                            >
                                <div className="relative z-10">
                                    <div className="text-4xl mb-4 inline-block transform transition-transform duration-300 group-hover:scale-110">
                                        {icon}
                                    </div>

                                    <h3 className="font-bold text-white mb-3 text-lg transition-colors duration-300">
                                        {title}
                                    </h3>

                                    <p className="text-sm text-gray-500 leading-relaxed group-hover:text-gray-400 transition-colors">
                                        {desc}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Why SkillSync Section */}
            <section className="py-24 bg-gray-950 border-t border-gray-900">
                <div className="container mx-auto px-6">
                    <div className="mb-16">
                        <h2 className="text-3xl font-black text-white mb-4">Why SkillSync</h2>
                        <p className="text-gray-500 font-light">Superior matching through semantic AI</p>
                    </div>

                    <div className="max-w-5xl mx-auto">
                        <div className="grid md:grid-cols-2 gap-8">
                            {/* Traditional Approach */}
                            <div className="group p-8 rounded-xl border border-gray-800 bg-black hover:border-gray-600 transition-all duration-300">
                                <h4 className="text-gray-400 font-bold text-lg mb-4 flex items-center gap-3">
                                    <span className="text-xl">❌</span>
                                    Keyword Matching
                                </h4>
                                <ul className="space-y-3 text-sm text-gray-600">
                                    <li className="flex gap-3">
                                        <span className="text-gray-700 flex-shrink-0">•</span>
                                        <span>Exact string matching only</span>
                                    </li>
                                    <li className="flex gap-3">
                                        <span className="text-gray-700 flex-shrink-0">•</span>
                                        <span>Cannot understand context or synonyms</span>
                                    </li>
                                    <li className="flex gap-3">
                                        <span className="text-gray-700 flex-shrink-0">•</span>
                                        <span>High false-negative rate</span>
                                    </li>
                                    <li className="flex gap-3">
                                        <span className="text-gray-700 flex-shrink-0">•</span>
                                        <span>"Python Dev" ≠ "Python Engineer"</span>
                                    </li>
                                </ul>
                            </div>

                            {/* SkillSync Approach */}
                            <div className="group p-8 rounded-xl border border-gray-700 bg-gray-900 hover:border-gray-500 transition-all duration-300">
                                <h4 className="text-white font-bold text-lg mb-4 flex items-center gap-3">
                                    <span className="text-xl">✅</span>
                                    SkillSync AI
                                </h4>
                                <ul className="space-y-3 text-sm text-gray-400">
                                    <li className="flex gap-3">
                                        <span className="text-gray-500 flex-shrink-0">•</span>
                                        <span>Understands semantic meaning</span>
                                    </li>
                                    <li className="flex gap-3">
                                        <span className="text-gray-500 flex-shrink-0">•</span>
                                        <span>384-dimensional vector space</span>
                                    </li>
                                    <li className="flex gap-3">
                                        <span className="text-gray-500 flex-shrink-0">•</span>
                                        <span>Handles synonyms and context</span>
                                    </li>
                                    <li className="flex gap-3">
                                        <span className="text-gray-500 flex-shrink-0">•</span>
                                        <span>Intelligent skill-to-job matching</span>
                                    </li>
                                </ul>
                            </div>
                        </div>

                        <div className="mt-12 p-6 rounded-xl border border-gray-800 bg-black">
                            <p className="text-sm text-gray-500 text-center">
                                <span className="font-semibold text-gray-400">AI Model:</span>
                                <code className="ml-2 px-3 py-1 rounded bg-gray-900 text-gray-300 font-mono text-xs">
                                    sentence-transformers/all-MiniLM-L6-v2
                                </code>
                            </p>
                            <p className="text-xs text-gray-600 text-center mt-3">
                                80M parameters · 384 output dimensions · ~5ms inference per document
                            </p>
                        </div>
                    </div>
                </div>
            </section>
        </>
    )
}
