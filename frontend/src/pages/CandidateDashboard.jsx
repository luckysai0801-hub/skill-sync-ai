/**
 * pages/CandidateDashboard.jsx – Full candidate dashboard.
 *
 * Sections:
 * 1. Resume Upload (drag-and-drop PDF)
 * 2. Ranked Jobs (top 5 matches)
 * 3. Score Breakdown (explainable AI)
 * 4. Skill Gap Analysis
 * 5. Resume Score
 * 6. Interview Probability
 */
import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import {
    uploadResume,
    matchJobs,
    getSkillGap,
    getResumeScore,
    getResume,
    getInterviewProbability,
    listJobs,
} from '../services/api'
import JobCard from '../components/JobCard'
import ScoreBreakdown from '../components/ScoreBreakdown'
import SkillGapPanel from '../components/SkillGapPanel'
import ResumeScorePanel from '../components/ResumeScorePanel'

const DEMO_CANDIDATE_IDS = [1, 2, 3, 4, 5]   // Demo resume IDs from seeded data
const DEMO_JOB_IDS = [1, 2, 3, 4, 5]

export default function CandidateDashboard() {
    const [step, setStep] = useState('upload')   // 'upload' | 'results'
    const [loading, setLoading] = useState(false)
    const [resumeId, setResumeId] = useState(null)
    const [matches, setMatches] = useState([])
    const [selectedMatch, setSelectedMatch] = useState(null)
    const [skillGap, setSkillGap] = useState(null)
    const [interviewProb, setInterviewProb] = useState(null)
    const [resumeScore, setResumeScore] = useState(null)
    const [resumeData, setResumeData] = useState(null)
    const [detailLoading, setDetailLoading] = useState(false)


    // ── Drag-and-drop PDF upload ───────────────────────────────────────────────
    const onDrop = useCallback(async (accepted) => {
        if (!accepted.length) return
        const file = accepted[0]
        if (!file.name.endsWith('.pdf')) {
            toast.error('Please upload a PDF file.')
            return
        }

        setLoading(true)
        toast.loading('Parsing resume with AI…', { id: 'upload' })
            try {
            // User ID 3 = first candidate in seeded data; real app would use auth
            const resume = await uploadResume(3, file)
            setResumeId(resume.id)
            setResumeData(resume)
            // resume returned from upload includes resume_score and authenticity
            setResumeScore(resume)

            toast.loading('Computing semantic matches…', { id: 'upload' })
            const jobMatches = await matchJobs(resume.id)
            setMatches(jobMatches)

            toast.success('Analysis complete!', { id: 'upload' })
            setStep('results')
        } catch (e) {
            toast.error(e?.response?.data?.detail || 'Upload failed.', { id: 'upload' })
        } finally {
            setLoading(false)
        }
    }, [])

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'application/pdf': ['.pdf'] },
        maxFiles: 1,
        disabled: loading,
    })

    // ── Demo mode: use seeded data without PDF upload ──────────────────────────
    const loadDemo = async (candidateId = 1) => {
        setLoading(true)
        toast.loading('Loading demo profile…', { id: 'demo' })
        try {
            setResumeId(candidateId)
            const [jobMatches, score, resumeFull] = await Promise.all([
                matchJobs(candidateId),
                getResumeScore(candidateId),
                getResume(candidateId),
            ])
            setMatches(jobMatches)
            setResumeScore(resumeFull)
            setResumeData(resumeFull)
            toast.success('Demo loaded!', { id: 'demo' })
            setStep('results')
        } catch (e) {
            toast.error('Demo load failed. Ensure backend is running.', { id: 'demo' })
        } finally {
            setLoading(false)
        }
    }

    // ── Select a job match to see full details ─────────────────────────────────
    const selectMatch = async (match) => {
        setSelectedMatch(match)
        setDetailLoading(true)
        setSkillGap(null)
        setInterviewProb(null)
        try {
            const [gap, prob] = await Promise.all([
                getSkillGap(resumeId, match.job_id),
                getInterviewProbability(resumeId, match.job_id),
            ])
            setSkillGap(gap)
            setInterviewProb(prob)
        } catch (e) {
            toast.error('Could not load details.')
        } finally {
            setDetailLoading(false)
        }
    }

    return (
        <div className="min-h-screen pt-20 bg-darkBg">
            <div className="max-w-4xl mx-auto px-6 py-8">
                {/* Header */}
                <div className="mb-8 animate-fade-in text-center">
                    <h1 className="text-4xl font-display font-black gradient-text mb-2">Your AI Profile</h1>
                    <p className="text-slate-400">Upload your resume to see how you rank against top opportunities.</p>
                </div>

                {/* ── UPLOAD STEP ────────────────────────────────────────────────── */}
                {step === 'upload' && (
                    <div className="max-w-2xl mx-auto animate-slide-up">
                        {/* Drop zone */}
                        <div
                            {...getRootProps()}
                            className={`rounded-2xl border-2 border-dashed p-16 text-center cursor-pointer transition-all duration-200 ${isDragActive
                                    ? 'border-brand-500 bg-brand-600/10'
                                    : 'border-white/20 hover:border-brand-500/50 hover:bg-white/2'
                                } ${loading ? 'opacity-50 pointer-events-none' : ''}`}
                        >
                            <input {...getInputProps()} />
                            <div className="text-6xl mb-4">📄</div>
                            <h2 className="text-2xl font-display font-bold text-white mb-2">
                                {isDragActive ? 'Drop your resume here!' : 'Upload Your Resume'}
                            </h2>
                            <p className="text-slate-400 mb-6">Drag & drop a PDF file, or click to browse</p>
                            {loading ? (
                                <div className="flex items-center justify-center gap-3 text-brand-300">
                                    <div className="spinner" /> Processing with AI…
                                </div>
                            ) : (
                                <button className="btn-brand">
                                    Choose PDF File
                                </button>
                            )}
                        </div>

                        {/* Demo buttons */}
                        <div className="mt-8 glass-card p-6">
                            <p className="text-sm text-slate-400 mb-4 text-center">
                                🚀 Or try with a demo profile (no file upload needed)
                            </p>
                            <div className="grid grid-cols-5 gap-2">
                                {DEMO_CANDIDATE_IDS.map((id) => (
                                    <button
                                        key={id}
                                        onClick={() => loadDemo(id)}
                                        disabled={loading}
                                        className="btn-secondary py-2 px-3 text-sm"
                                    >
                                        Demo #{id}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* ── RESULTS STEP ───────────────────────────────────────────────── */}
                {step === 'results' && (
                    <div className="animate-fade-in">
                        {/* Back button */}
                        <div className="flex items-center gap-4 mb-8">
                            <button onClick={() => { setStep('upload'); setSelectedMatch(null) }}
                                className="btn-secondary py-2 px-4 text-sm flex items-center gap-2">
                                ← Upload Another
                            </button>
                            <span className="text-slate-400 text-sm">Resume ID: #{resumeId}</span>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                            {/* ── Left column: Matched Jobs ────────────────────────────── */}
                            <div className="xl:col-span-1">
                                <h2 className="section-header">🎯 Top Matched Jobs</h2>
                                <div className="space-y-4">
                                    {matches.length === 0 && (
                                        <div className="glass-card p-6 text-center text-slate-400">
                                            No matches found. Check if the backend is running.
                                        </div>
                                    )}
                                    {matches.map((m) => (
                                        <JobCard
                                            key={m.job_id}
                                            match={m}
                                            selected={selectedMatch?.job_id === m.job_id}
                                            onSelect={selectMatch}
                                        />
                                    ))}
                                </div>
                            </div>

                            {/* ── Middle column: Score + Skill Gap ────────────────────── */}
                            <div className="xl:col-span-1 space-y-6">
                                {selectedMatch ? (
                                    <>
                                        <h2 className="section-header">📊 AI Score Breakdown</h2>
                                        <ScoreBreakdown scores={selectedMatch.scores} />

                                        {detailLoading && (
                                            <div className="glass-card p-6 text-center">
                                                <div className="spinner mx-auto mb-2" />
                                                <p className="text-slate-400 text-sm">Analyzing skill gaps…</p>
                                            </div>
                                        )}

                                        {skillGap && !detailLoading && (
                                            <SkillGapPanel gap={skillGap} />
                                        )}

                                        {interviewProb && !detailLoading && (
                                            <div className="glass-card p-6">
                                                <h3 className="font-display font-bold text-white mb-4 flex items-center gap-2">
                                                    <span className="text-xl">🎲</span> Interview Probability
                                                </h3>
                                                <div className="text-center">
                                                    <div className="text-6xl font-display font-black mb-2"
                                                        style={{
                                                            background: 'linear-gradient(135deg, #10b981, #34d399)',
                                                            WebkitBackgroundClip: 'text',
                                                            WebkitTextFillColor: 'transparent',
                                                        }}>
                                                        {interviewProb.interview_probability?.toFixed(1)}%
                                                    </div>
                                                    <p className="text-slate-400 text-sm">
                                                        Based on your match score and skill market demand
                                                    </p>
                                                </div>
                                                <div className="progress-bar mt-4">
                                                    <div
                                                        className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-teal-400"
                                                        style={{ width: `${interviewProb.interview_probability}%` }}
                                                    />
                                                </div>
                                            </div>
                                        )}
                                    </>
                                ) : (
                                    <div className="glass-card p-8 text-center">
                                        <div className="text-4xl mb-3">👈</div>
                                        <p className="text-slate-400">Select a job to see detailed AI analysis</p>
                                    </div>
                                )}
                            </div>

                            {/* ── Right column: Resume Score ───────────────────────────── */}
                            <div className="xl:col-span-1">
                                <h2 className="section-header">📄 Resume Quality</h2>
                                {resumeScore ? (
                                    <ResumeScorePanel scoreData={resumeScore} />
                                ) : (
                                    <div className="glass-card p-6 text-center text-slate-400">
                                        Resume score loading…
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
