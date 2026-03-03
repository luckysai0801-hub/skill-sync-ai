/**
 * components/ResumeScorePanel.jsx – Resume quality score display.
 */
import React from 'react'

export default function ResumeScorePanel({ scoreData, className = '' }) {
    if (!scoreData) return null

    const score = scoreData.resume_score || 0
    const suggestions = scoreData.improvement_suggestions || []

    const getLabel = (s) => s >= 80 ? '🏆 Excellent' : s >= 60 ? '✅ Good' : s >= 40 ? '⚠️ Needs Work' : '❗ Poor'
    const getLabelColor = (s) => s >= 80 ? 'text-emerald-400' : s >= 60 ? 'text-blue-400' : s >= 40 ? 'text-amber-400' : 'text-rose-400'

    return (
        <div className={`glass-card p-6 ${className}`}>
            <h3 className="font-display font-bold text-white mb-5 flex items-center gap-2">
                <span className="text-xl">📄</span> Resume Quality Score
            </h3>

            {/* Big score */}
            <div className="text-center mb-6">
                <div className="inline-flex items-center justify-center w-28 h-28 rounded-full mb-3"
                    style={{
                        background: 'conic-gradient(#6366f1 0%, #8b5cf6 ' + score + '%, rgba(255,255,255,0.08) ' + score + '%)',
                        padding: 5,
                    }}>
                    <div className="w-full h-full rounded-full flex flex-col items-center justify-center"
                        style={{ background: '#0f0f1a' }}>
                        <span className="text-3xl font-display font-bold gradient-text">{score.toFixed(0)}</span>
                        <span className="text-xs text-slate-400">/ 100</span>
                    </div>
                </div>
                <p className={`font-semibold ${getLabelColor(score)}`}>{getLabel(score)}</p>
            </div>

            {/* Authenticity indicator */}
            {scoreData.authenticity_score !== undefined && scoreData.authenticity_score !== null && (
                <div className="mt-4 p-4 rounded-lg" style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.04)' }}>
                    <p className="text-sm text-slate-400 mb-2">🔎 Authenticity</p>
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-bold text-white text-lg">{(scoreData.authenticity_score || 0).toFixed(0)}%</p>
                            <p className="text-sm text-slate-400">{scoreData.authenticity_label || 'Unknown'}</p>
                        </div>
                        <div className="text-right text-sm text-slate-400 max-w-xs">
                            {scoreData.authenticity_explanation || 'No explanation available.'}
                        </div>
                    </div>
                </div>
            )}

            {/* Scored dimensions */}
            {scoreData.breakdown && (
                <div className="grid grid-cols-2 gap-3 mb-6">
                    {[
                        { label: 'Achievements', key: 'achievements_score', max: 25 },
                        { label: 'Action Verbs', key: 'action_verbs_score', max: 25 },
                        { label: 'Skill Clarity', key: 'skill_clarity_score', max: 25 },
                        { label: 'Keywords', key: 'keyword_density_score', max: 25 },
                    ].map(({ label, key, max }) => (
                        <div key={key} className="rounded-xl p-3"
                            style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)' }}>
                            <p className="text-xs text-slate-400 mb-1">{label}</p>
                            <p className="font-bold text-brand-300 text-lg">
                                {(scoreData.breakdown[key] || 0).toFixed(0)}
                                <span className="text-xs text-slate-500 font-normal">/{max}</span>
                            </p>
                        </div>
                    ))}
                </div>
            )}

            {/* Improvement suggestions */}
            {suggestions.length > 0 && (
                <div>
                    <p className="text-sm font-semibold text-slate-300 mb-3">💡 Improvement Suggestions</p>
                    <ul className="space-y-2">
                        {suggestions.map((s, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-slate-400">
                                <span className="text-brand-400 mt-0.5 flex-shrink-0">→</span>
                                {s}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    )
}
