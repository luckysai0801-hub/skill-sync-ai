/**
 * pages/EmployerDashboard.jsx – Employer view with job creation and candidate ranking.
 */
import React, { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import { createJob, listJobs, matchCandidates } from '../services/api'
import CandidateCard from '../components/CandidateCard'

const DEMO_JOB_IDS = [1, 2, 3, 4, 5]

const SKILL_OPTIONS = [
    'python', 'javascript', 'typescript', 'react', 'node.js', 'fastapi', 'django',
    'postgresql', 'mongodb', 'docker', 'kubernetes', 'aws', 'gcp', 'azure',
    'machine learning', 'deep learning', 'pytorch', 'tensorflow', 'scikit-learn',
    'java', 'spring boot', 'sql', 'redis', 'kafka', 'git', 'linux', 'rest api',
]

const defaultForm = {
    employer_id: 2, // demo employer ID
    title: '',
    description: '',
    required_skills: [],
    required_experience: 3,
    salary_min: 80000,
    salary_max: 120000,
    location_city: '',
    location_state: '',
    is_remote: false,
}

export default function EmployerDashboard() {
    const [tab, setTab] = useState('rank')   // 'rank' | 'create'
    const [form, setForm] = useState(defaultForm)
    const [skillInput, setSkillInput] = useState('')
    const [submitting, setSubmitting] = useState(false)
    const [selectedJobId, setSelectedJobId] = useState(null)
    const [candidates, setCandidates] = useState([])
    const [loadingCandidates, setLoadingCandidates] = useState(false)
    const [jobs, setJobs] = useState([])

    useEffect(() => {
        listJobs().then(setJobs).catch(() => { })
    }, [])

    // ── Load candidates for a job ──────────────────────────────────────────────
    const loadCandidates = async (jobId) => {
        setSelectedJobId(jobId)
        setLoadingCandidates(true)
        setCandidates([])
        try {
            const result = await matchCandidates(jobId)
            setCandidates(result)
        } catch (e) {
            toast.error('Could not load candidates.')
        } finally {
            setLoadingCandidates(false)
        }
    }

    // ── Add skill tag ─────────────────────────────────────────────────────────
    const addSkill = (skill) => {
        const s = skill.trim().toLowerCase()
        if (s && !form.required_skills.includes(s)) {
            setForm(f => ({ ...f, required_skills: [...f.required_skills, s] }))
        }
        setSkillInput('')
    }

    const removeSkill = (skill) => {
        setForm(f => ({ ...f, required_skills: f.required_skills.filter(s => s !== skill) }))
    }

    // ── Submit new job ─────────────────────────────────────────────────────────
    const handleSubmit = async (e) => {
        e.preventDefault()
        if (!form.title || !form.description) {
            toast.error('Title and description are required.')
            return
        }
        setSubmitting(true)
        toast.loading('Creating job posting…', { id: 'job' })
        try {
            const job = await createJob({
                ...form,
                required_experience: parseFloat(form.required_experience),
                salary_min: parseFloat(form.salary_min),
                salary_max: parseFloat(form.salary_max),
            })
            toast.success(`Job "${job.title}" created! ID: ${job.id}`, { id: 'job' })
            setForm(defaultForm)
            const updated = await listJobs()
            setJobs(updated)
            setTab('rank')
        } catch (e) {
            toast.error(e?.response?.data?.detail || 'Job creation failed.', { id: 'job' })
        } finally {
            setSubmitting(false)
        }
    }

    return (
        <div className="min-h-screen pt-20">
            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Header */}
                <div className="mb-8 animate-fade-in">
                    <h1 className="text-4xl font-display font-black gradient-text mb-2">Employer Dashboard</h1>
                    <p className="text-slate-400">Find top candidates or post new job opportunities</p>
                </div>

                {/* Tab nav */}
                <div className="flex gap-2 mb-8 p-1 rounded-xl w-fit"
                    style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)' }}>
                    {[
                        { id: 'rank', label: '🏆 Rank Candidates' },
                        { id: 'create', label: '➕ Post a Job' },
                    ].map(({ id, label }) => (
                        <button
                            key={id}
                            onClick={() => setTab(id)}
                            className={`px-5 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${tab === id
                                    ? 'text-white'
                                    : 'text-slate-400 hover:text-white'
                                }`}
                            style={tab === id ? { background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' } : {}}
                        >
                            {label}
                        </button>
                    ))}
                </div>

                {/* ── RANK TAB ──────────────────────────────────────────────────── */}
                {tab === 'rank' && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in">
                        {/* Job selector */}
                        <div className="lg:col-span-1">
                            <h2 className="section-header">Select Job</h2>
                            <div className="space-y-3">
                                {/* Demo quick load */}
                                <div className="glass-card p-4">
                                    <p className="text-xs text-slate-500 mb-3">Quick select demo jobs:</p>
                                    <div className="grid grid-cols-5 gap-1.5">
                                        {DEMO_JOB_IDS.map((id) => (
                                            <button
                                                key={id}
                                                onClick={() => loadCandidates(id)}
                                                className={`py-1.5 text-xs rounded-lg font-medium transition-all ${selectedJobId === id
                                                        ? 'text-white'
                                                        : 'text-slate-400 hover:text-white'
                                                    }`}
                                                style={selectedJobId === id
                                                    ? { background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }
                                                    : { background: 'rgba(255,255,255,0.05)' }}
                                            >
                                                Job {id}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                {/* Job list */}
                                {jobs.slice(0, 10).map((job) => (
                                    <button
                                        key={job.id}
                                        onClick={() => loadCandidates(job.id)}
                                        className={`w-full text-left glass-card p-4 transition-all duration-200 ${selectedJobId === job.id ? 'border-brand-500/50' : ''
                                            }`}
                                        style={selectedJobId === job.id
                                            ? { borderColor: 'rgba(99,102,241,0.5)', boxShadow: '0 0 15px rgba(99,102,241,0.15)' }
                                            : {}}
                                    >
                                        <p className="font-semibold text-white text-sm">{job.title}</p>
                                        <p className="text-xs text-slate-400 mt-1">
                                            {job.is_remote ? '🌍 Remote' : `📍 ${job.location_city}`} ·
                                            ${(job.salary_min / 1000).toFixed(0)}k–${(job.salary_max / 1000).toFixed(0)}k
                                        </p>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Candidate list */}
                        <div className="lg:col-span-2">
                            <h2 className="section-header">🏅 Top Ranked Candidates</h2>
                            {!selectedJobId && (
                                <div className="glass-card p-8 text-center">
                                    <div className="text-4xl mb-3">👈</div>
                                    <p className="text-slate-400">Select a job to view top candidates</p>
                                </div>
                            )}
                            {loadingCandidates && (
                                <div className="glass-card p-8 text-center">
                                    <div className="spinner mx-auto mb-3" />
                                    <p className="text-slate-400 text-sm">Running AI matching engine…</p>
                                </div>
                            )}
                            {!loadingCandidates && candidates.length > 0 && (
                                <div className="space-y-4 animate-fade-in">
                                    {candidates.map((c, i) => (
                                        <CandidateCard key={c.match_id} match={c} rank={i + 1} />
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* ── CREATE JOB TAB ────────────────────────────────────────────── */}
                {tab === 'create' && (
                    <div className="max-w-3xl mx-auto animate-slide-up">
                        <div className="glass-card p-8">
                            <h2 className="text-2xl font-display font-bold text-white mb-6">Post a New Job</h2>
                            <form onSubmit={handleSubmit} className="space-y-6">
                                {/* Title */}
                                <div>
                                    <label className="text-sm font-medium text-slate-300 mb-2 block">Job Title *</label>
                                    <input
                                        className="input-field"
                                        placeholder="e.g. Senior Python Engineer"
                                        value={form.title}
                                        onChange={(e) => setForm(f => ({ ...f, title: e.target.value }))}
                                        required
                                    />
                                </div>

                                {/* Description */}
                                <div>
                                    <label className="text-sm font-medium text-slate-300 mb-2 block">Job Description *</label>
                                    <textarea
                                        className="input-field resize-none"
                                        rows={5}
                                        placeholder="Describe the role, responsibilities, and what you're looking for…"
                                        value={form.description}
                                        onChange={(e) => setForm(f => ({ ...f, description: e.target.value }))}
                                        required
                                    />
                                </div>

                                {/* Skills */}
                                <div>
                                    <label className="text-sm font-medium text-slate-300 mb-2 block">Required Skills</label>
                                    <div className="flex flex-wrap gap-2 mb-3">
                                        {form.required_skills.map((s) => (
                                            <span key={s} className="skill-tag flex items-center gap-1 cursor-pointer"
                                                onClick={() => removeSkill(s)}>
                                                {s} <span className="text-rose-400">×</span>
                                            </span>
                                        ))}
                                    </div>
                                    <div className="flex gap-2">
                                        <input
                                            className="input-field"
                                            list="skill-suggestions"
                                            placeholder="Type a skill and press Enter…"
                                            value={skillInput}
                                            onChange={(e) => setSkillInput(e.target.value)}
                                            onKeyDown={(e) => {
                                                if (e.key === 'Enter') { e.preventDefault(); addSkill(skillInput) }
                                            }}
                                        />
                                        <datalist id="skill-suggestions">
                                            {SKILL_OPTIONS.map(s => <option key={s} value={s} />)}
                                        </datalist>
                                        <button type="button" onClick={() => addSkill(skillInput)} className="btn-secondary px-4 py-2 text-sm flex-shrink-0">
                                            Add
                                        </button>
                                    </div>
                                </div>

                                {/* Experience + Salary */}
                                <div className="grid grid-cols-3 gap-4">
                                    <div>
                                        <label className="text-sm font-medium text-slate-300 mb-2 block">Min Experience (yrs)</label>
                                        <input type="number" className="input-field" min={0} step={0.5}
                                            value={form.required_experience}
                                            onChange={(e) => setForm(f => ({ ...f, required_experience: e.target.value }))} />
                                    </div>
                                    <div>
                                        <label className="text-sm font-medium text-slate-300 mb-2 block">Salary Min ($)</label>
                                        <input type="number" className="input-field" min={0}
                                            value={form.salary_min}
                                            onChange={(e) => setForm(f => ({ ...f, salary_min: e.target.value }))} />
                                    </div>
                                    <div>
                                        <label className="text-sm font-medium text-slate-300 mb-2 block">Salary Max ($)</label>
                                        <input type="number" className="input-field" min={0}
                                            value={form.salary_max}
                                            onChange={(e) => setForm(f => ({ ...f, salary_max: e.target.value }))} />
                                    </div>
                                </div>

                                {/* Location */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="text-sm font-medium text-slate-300 mb-2 block">City</label>
                                        <input className="input-field" placeholder="e.g. San Francisco"
                                            value={form.location_city}
                                            onChange={(e) => setForm(f => ({ ...f, location_city: e.target.value }))} />
                                    </div>
                                    <div>
                                        <label className="text-sm font-medium text-slate-300 mb-2 block">State</label>
                                        <input className="input-field" placeholder="e.g. California"
                                            value={form.location_state}
                                            onChange={(e) => setForm(f => ({ ...f, location_state: e.target.value }))} />
                                    </div>
                                </div>

                                {/* Remote toggle */}
                                <div className="flex items-center gap-3">
                                    <button
                                        type="button"
                                        onClick={() => setForm(f => ({ ...f, is_remote: !f.is_remote }))}
                                        className={`w-12 h-6 rounded-full transition-all duration-200 flex items-center px-0.5 ${form.is_remote ? 'bg-brand-600' : 'bg-white/20'
                                            }`}
                                    >
                                        <div className={`w-5 h-5 rounded-full bg-white shadow transition-transform duration-200 ${form.is_remote ? 'translate-x-6' : 'translate-x-0'
                                            }`} />
                                    </button>
                                    <label className="text-sm text-slate-300">Remote / Work from Home</label>
                                </div>

                                {/* Submit */}
                                <button
                                    type="submit"
                                    disabled={submitting}
                                    className="btn-brand w-full py-4 text-base flex items-center justify-center gap-2"
                                >
                                    {submitting ? (
                                        <><div className="spinner border-white/30 border-t-white" /> Creating…</>
                                    ) : (
                                        '🚀 Post Job & Generate AI Embedding'
                                    )}
                                </button>
                            </form>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
