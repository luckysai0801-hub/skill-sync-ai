/**
 * pages/AnalyticsDashboard.jsx – Recruiter analytics with Recharts charts.
 *
 * Displays:
 * • Average candidate score (stat)
 * • Total candidates (stat)
 * • Top 5 candidates (ranked list)
 * • Skill distribution (bar chart)
 * • Experience distribution (pie chart)
 * • Score distribution (area chart)
 */
import React, { useState } from 'react'
import toast from 'react-hot-toast'
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, Legend,
    AreaChart, Area, CartesianGrid,
} from 'recharts'
import { getRecruiterDashboard } from '../services/api'
import CandidateCard from '../components/CandidateCard'

const JOB_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

const PIE_COLORS = ['#6366f1', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899']

const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null
    return (
        <div className="rounded-xl px-4 py-3 text-sm"
            style={{ background: 'rgba(26,26,46,0.95)', border: '1px solid rgba(99,102,241,0.3)' }}>
            <p className="text-slate-300 font-medium">{label}</p>
            {payload.map((p, i) => (
                <p key={i} className="font-bold" style={{ color: p.color }}>{p.value}</p>
            ))}
        </div>
    )
}

export default function AnalyticsDashboard() {
    const [selectedJobId, setSelectedJobId] = useState(null)
    const [dashboard, setDashboard] = useState(null)
    const [loading, setLoading] = useState(false)

    const loadDashboard = async (jobId) => {
        setSelectedJobId(jobId)
        setLoading(true)
        setDashboard(null)
        toast.loading(`Loading analytics for Job #${jobId}…`, { id: 'dash' })
        try {
            const data = await getRecruiterDashboard(jobId)
            setDashboard(data)
            toast.success('Dashboard loaded!', { id: 'dash' })
        } catch (e) {
            toast.error('Failed to load dashboard.', { id: 'dash' })
        } finally {
            setLoading(false)
        }
    }

    // Prepare chart data
    const skillChartData = dashboard
        ? Object.entries(dashboard.skill_distribution).map(([name, value]) => ({ name, value }))
        : []

    const expChartData = dashboard
        ? Object.entries(dashboard.experience_distribution).map(([range, count]) => ({
            name: range + ' yrs', value: count
        })).filter(d => d.value > 0)
        : []

    // Simulated score distribution for area chart
    const scoreDistData = dashboard?.top_candidates
        ? dashboard.top_candidates.map((c, i) => ({
            name: `#${i + 1}`,
            score: c.scores?.final_score || 0,
            interview: c.interview_probability || 0,
        }))
        : []

    return (
        <div className="min-h-screen pt-20">
            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Header */}
                <div className="mb-8 animate-fade-in">
                    <h1 className="text-4xl font-display font-black gradient-text mb-2">Recruiter Analytics</h1>
                    <p className="text-slate-400">Deep insights into candidate pool quality and skill distribution</p>
                </div>

                {/* Job picker */}
                <div className="glass-card p-5 mb-8">
                    <p className="text-sm text-slate-400 mb-3">Select a job to analyze:</p>
                    <div className="flex flex-wrap gap-2">
                        {JOB_IDS.map((id) => (
                            <button
                                key={id}
                                onClick={() => loadDashboard(id)}
                                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${selectedJobId === id ? 'text-white' : 'text-slate-400 hover:text-white'
                                    }`}
                                style={selectedJobId === id
                                    ? { background: 'linear-gradient(135deg,#6366f1,#8b5cf6)' }
                                    : { background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)' }}
                            >
                                Job #{id}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Loading */}
                {loading && (
                    <div className="glass-card p-16 text-center animate-fade-in">
                        <div className="spinner w-10 h-10 mx-auto mb-4 border-4" />
                        <p className="text-slate-400">Running AI analysis across all candidates…</p>
                    </div>
                )}

                {/* Dashboard content */}
                {dashboard && !loading && (
                    <div className="animate-fade-in space-y-8">
                        {/* Stat cards */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <StatCard value={dashboard.total_candidates} label="Total Candidates" icon="👥" />
                            <StatCard value={dashboard.average_score?.toFixed(1)} label="Avg Match Score" icon="🎯" />
                            <StatCard value={dashboard.top_candidates?.length} label="Top Ranked" icon="🏅" />
                            <StatCard
                                value={Object.keys(dashboard.skill_distribution).length}
                                label="Unique Skills"
                                icon="⚡"
                            />
                        </div>

                        {/* Job info */}
                        <div className="glass-card p-5">
                            <h2 className="font-display font-bold text-xl text-white">{dashboard.job_title}</h2>
                            <p className="text-sm text-slate-400 mt-1">Job ID #{dashboard.job_id} · {dashboard.total_candidates} candidates analyzed</p>
                        </div>

                        {/* Top candidates */}
                        <div>
                            <h2 className="section-header">🏆 Top 5 Candidates</h2>
                            <div className="space-y-3">
                                {dashboard.top_candidates?.map((c, i) => (
                                    <CandidateCard key={c.match_id} match={c} rank={i + 1} />
                                ))}
                            </div>
                        </div>

                        {/* Charts row */}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {/* Skill distribution bar chart */}
                            <div className="glass-card p-6">
                                <h3 className="font-display font-bold text-white mb-1">📊 Skill Distribution</h3>
                                <p className="text-xs text-slate-500 mb-5">Most common skills across all candidates</p>
                                <ResponsiveContainer width="100%" height={260}>
                                    <BarChart data={skillChartData.slice(0, 10)} layout="vertical" margin={{ left: 40, right: 20 }}>
                                        <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }} />
                                        <YAxis type="category" dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} width={80} />
                                        <Tooltip content={<CustomTooltip />} />
                                        <Bar dataKey="value" fill="#6366f1" radius={[0, 4, 4, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>

                            {/* Experience distribution pie */}
                            <div className="glass-card p-6">
                                <h3 className="font-display font-bold text-white mb-1">🎓 Experience Distribution</h3>
                                <p className="text-xs text-slate-500 mb-5">Years of experience across candidate pool</p>
                                <ResponsiveContainer width="100%" height={260}>
                                    <PieChart>
                                        <Pie
                                            data={expChartData}
                                            cx="50%" cy="50%"
                                            innerRadius={60}
                                            outerRadius={100}
                                            paddingAngle={4}
                                            dataKey="value"
                                            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                            labelLine={false}
                                        >
                                            {expChartData.map((_, i) => (
                                                <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip content={<CustomTooltip />} />
                                        <Legend wrapperStyle={{ color: '#94a3b8', fontSize: 12 }} />
                                    </PieChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Score vs interview probability area chart */}
                        <div className="glass-card p-6">
                            <h3 className="font-display font-bold text-white mb-1">📈 Score vs Interview Probability</h3>
                            <p className="text-xs text-slate-500 mb-5">Top candidates ranked by AI match score</p>
                            <ResponsiveContainer width="100%" height={220}>
                                <AreaChart data={scoreDistData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                                    <defs>
                                        <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                                            <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="interviewGrad" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                                            <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid stroke="rgba(255,255,255,0.04)" />
                                    <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} />
                                    <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
                                    <Tooltip content={<CustomTooltip />} />
                                    <Area type="monotone" dataKey="score" stroke="#6366f1" fill="url(#scoreGrad)" strokeWidth={2} name="Match Score" />
                                    <Area type="monotone" dataKey="interview" stroke="#10b981" fill="url(#interviewGrad)" strokeWidth={2} name="Interview %" />
                                    <Legend wrapperStyle={{ color: '#94a3b8', fontSize: 12 }} />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                )}

                {/* Empty state */}
                {!dashboard && !loading && (
                    <div className="glass-card p-16 text-center">
                        <div className="text-5xl mb-4">📊</div>
                        <h3 className="font-display font-bold text-xl text-white mb-2">Select a Job to Begin</h3>
                        <p className="text-slate-400">Click any job number above to run AI analytics on all candidates.</p>
                    </div>
                )}
            </div>
        </div>
    )
}

function StatCard({ value, label, icon }) {
    return (
        <div className="glass-card p-5 text-center">
            <div className="text-2xl mb-2">{icon}</div>
            <div className="text-3xl font-display font-bold gradient-text">{value}</div>
            <div className="text-xs text-slate-400 mt-1 font-medium">{label}</div>
        </div>
    )
}
