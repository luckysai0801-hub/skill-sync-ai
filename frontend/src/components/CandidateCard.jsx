/**
 * components/CandidateCard.jsx – Ranked candidate card for employer view.
 */
import React from 'react'

const getScoreColor = (score) => {
    if (score >= 75) return { color: '#10b981', bg: 'rgba(16,185,129,0.12)', border: 'rgba(16,185,129,0.25)' }
    if (score >= 50) return { color: '#f59e0b', bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.25)' }
    return { color: '#ef4444', bg: 'rgba(239,68,68,0.12)', border: 'rgba(239,68,68,0.25)' }
}

export default function CandidateCard({ match, rank }) {
    const scores = match?.scores
    const finalScore = scores?.final_score || 0
    const style = getScoreColor(finalScore)

    return (
        <div className="glass-card p-5 flex items-center gap-5 hover:border-brand-500/30 transition-all duration-200"
            style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
            {/* Rank */}
            <div className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold text-slate-400"
                style={{ background: 'rgba(255,255,255,0.05)' }}>
                #{rank}
            </div>

            {/* Avatar placeholder */}
            <div className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg flex-shrink-0"
                style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}>
                {String.fromCharCode(65 + ((match.resume_id - 1) % 26))}
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0">
                <p className="font-semibold text-white">Candidate #{match.resume_id}</p>
                <div className="flex items-center gap-3 mt-1">
                    {scores && (
                        <>
                            <span className="text-xs text-slate-400">
                                Skills: <span className="text-brand-300">{scores.skill_overlap?.toFixed(0)}%</span>
                            </span>
                            <span className="text-xs text-slate-400">
                                Exp: <span className="text-brand-300">{scores.experience_score?.toFixed(0)}%</span>
                            </span>
                        </>
                    )}
                </div>
                {/* Score bar */}
                <div className="mt-2 h-1 bg-white/10 rounded-full overflow-hidden">
                    <div
                        className="h-full rounded-full"
                        style={{
                            width: `${finalScore}%`,
                            background: `linear-gradient(90deg, ${style.color}, ${style.color}88)`,
                        }}
                    />
                </div>
            </div>

            {/* Score badge */}
            <div className="text-center flex-shrink-0">
                <div className="w-14 h-14 rounded-full flex items-center justify-center font-display font-bold text-lg"
                    style={{ background: style.bg, border: `2px solid ${style.border}`, color: style.color }}>
                    {finalScore.toFixed(0)}
                </div>
                <p className="text-xs text-slate-500 mt-1">score</p>
            </div>

            {/* Interview prob */}
            <div className="text-center hidden sm:block flex-shrink-0">
                <p className="text-lg font-bold text-emerald-400">{match.interview_probability?.toFixed(0)}%</p>
                <p className="text-xs text-slate-500">interview</p>
            </div>
        </div>
    )
}
