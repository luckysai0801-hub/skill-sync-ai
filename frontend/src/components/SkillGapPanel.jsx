/**
 * components/SkillGapPanel.jsx – Displays skill gaps and simulated score improvement.
 */
import React from 'react'

export default function SkillGapPanel({ gap, className = '' }) {
    if (!gap) return null

    const improvement = gap.simulated_score - gap.current_score

    return (
        <div className={`glass-card p-6 ${className}`}>
            <h3 className="font-display font-bold text-white mb-4 flex items-center gap-2">
                <span className="text-xl">🎯</span> Skill Gap Analysis
            </h3>

            {/* Score comparison */}
            <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="rounded-xl p-4 text-center"
                    style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)' }}>
                    <p className="text-2xl font-display font-bold text-rose-400">{gap.current_score?.toFixed(1)}</p>
                    <p className="text-xs text-slate-400 mt-1">Current Score</p>
                </div>
                <div className="rounded-xl p-4 text-center"
                    style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)' }}>
                    <p className="text-2xl font-display font-bold text-emerald-400">{gap.simulated_score?.toFixed(1)}</p>
                    <p className="text-xs text-slate-400 mt-1">After Upskilling</p>
                </div>
            </div>

            {improvement > 0 && (
                <div className="mb-5 px-4 py-3 rounded-xl flex items-center gap-3"
                    style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.15)' }}>
                    <span className="text-xl">⬆️</span>
                    <div>
                        <p className="text-sm font-semibold text-emerald-400">
                            +{improvement.toFixed(1)} point improvement possible
                        </p>
                        <p className="text-xs text-slate-400">by learning the missing skills below</p>
                    </div>
                </div>
            )}

            {/* Missing skills */}
            <div>
                <p className="text-sm font-semibold text-slate-300 mb-3">
                    Missing Skills
                    <span className="ml-2 text-xs text-rose-400">({gap.missing_skills?.length || 0} gaps)</span>
                </p>
                {gap.missing_skills?.length === 0 ? (
                    <div className="flex items-center gap-2 text-emerald-400 text-sm">
                        <span>✅</span>
                        <span>You have all required skills for this role!</span>
                    </div>
                ) : (
                    <div className="flex flex-wrap gap-2">
                        {gap.missing_skills?.map((skill) => (
                            <span key={skill} className="skill-tag missing flex items-center gap-1">
                                <span>❌</span> {skill}
                            </span>
                        ))}
                    </div>
                )}
            </div>

            {/* Demand weight */}
            {gap.skill_demand_weight && (
                <div className="mt-5 pt-4 border-t border-white/5">
                    <div className="flex justify-between items-center">
                        <span className="text-xs text-slate-400">Skill Market Demand</span>
                        <span className="text-xs font-bold text-brand-300">
                            {(gap.skill_demand_weight * 100).toFixed(0)}%
                        </span>
                    </div>
                    <div className="progress-bar mt-1.5">
                        <div
                            className="h-full rounded-full bg-gradient-to-r from-purple-500 to-pink-500"
                            style={{ width: `${gap.skill_demand_weight * 100}%` }}
                        />
                    </div>
                </div>
            )}
        </div>
    )
}
