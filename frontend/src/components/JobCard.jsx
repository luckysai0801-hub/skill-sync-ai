/**
 * components/JobCard.jsx – A single job match card with score ring.
 */
import React, { useState } from 'react'

const getScoreColor = (score) => {
    if (score >= 75) return { color: '#10b981', bg: 'rgba(16,185,129,0.15)', border: 'rgba(16,185,129,0.3)' }
    if (score >= 50) return { color: '#f59e0b', bg: 'rgba(245,158,11,0.15)', border: 'rgba(245,158,11,0.3)' }
    return { color: '#ef4444', bg: 'rgba(239,68,68,0.15)', border: 'rgba(239,68,68,0.3)' }
}

export default function JobCard({ match, job, onSelect, selected }) {
    const scores = match?.scores
    const finalScore = scores?.final_score || 0
    const colorStyle = getScoreColor(finalScore)

    return (
        <div
            onClick={() => onSelect && onSelect(match)}
            className={`glass-card p-5 cursor-pointer border transition-all duration-200 ${selected ? 'border-brand-500/60 shadow-glow' : ''
                }`}
            style={selected ? { borderColor: 'rgba(99,102,241,0.5)', boxShadow: '0 0 20px rgba(99,102,241,0.2)' } : {}}
        >
            <div className="flex items-start justify-between gap-4">
                {/* Left: Info */}
                <div className="flex-1 min-w-0">
                    <h3 className="font-display font-bold text-white truncate">
                        {match?.job_title || job?.title || 'Job Position'}
                    </h3>
                    <p className="text-sm text-slate-400 mt-1">
                        {job?.location_city && `${job.location_city}, ${job.location_state}`}
                        {job?.is_remote && <span className="ml-2 text-emerald-400 text-xs font-medium">• Remote</span>}
                    </p>

                    {/* Mini score bars */}
                    {scores && (
                        <div className="mt-3 space-y-1.5">
                            <MiniBar label="Semantic" value={scores.semantic_score} />
                            <MiniBar label="Skills" value={scores.skill_overlap} />
                        </div>
                    )}

                    {/* Interview probability */}
                    {match?.interview_probability !== undefined && (
                        <div className="mt-3 flex items-center gap-2">
                            <span className="text-xs text-slate-400">Interview probability:</span>
                            <span className="text-xs font-bold text-emerald-400">{match.interview_probability.toFixed(1)}%</span>
                        </div>
                    )}
                </div>

                {/* Right: Score circle */}
                <div className="flex-shrink-0">
                    <div
                        className="w-16 h-16 rounded-full flex items-center justify-center text-lg font-display font-bold"
                        style={{ background: colorStyle.bg, border: `2px solid ${colorStyle.border}`, color: colorStyle.color }}
                    >
                        {finalScore.toFixed(0)}
                    </div>
                </div>
            </div>

            {/* Missing skills preview */}
            {match?.missing_skills?.length > 0 && (
                <div className="mt-3 pt-3 border-t border-white/5">
                    <p className="text-xs text-slate-500 mb-1.5">Missing skills:</p>
                    <div className="flex flex-wrap gap-1">
                        {match.missing_skills.slice(0, 3).map((s) => (
                            <span key={s} className="skill-tag missing">{s}</span>
                        ))}
                        {match.missing_skills.length > 3 && (
                            <span className="text-xs text-slate-400">+{match.missing_skills.length - 3} more</span>
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}

function MiniBar({ label, value }) {
    return (
        <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 w-16 flex-shrink-0">{label}</span>
            <div className="flex-1 h-1 bg-white/10 rounded-full overflow-hidden">
                <div
                    className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-purple-500"
                    style={{ width: `${Math.min(100, value || 0)}%` }}
                />
            </div>
            <span className="text-xs text-slate-400 w-8 text-right">{(value || 0).toFixed(0)}%</span>
        </div>
    )
}
