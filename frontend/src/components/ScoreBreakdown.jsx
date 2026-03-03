/**
 * components/ScoreBreakdown.jsx
 * Visual explainable AI score breakdown using progress bars.
 */
import React from 'react'

const ScoreBar = ({ label, value, color = 'brand' }) => {
    const colorMap = {
        brand: 'from-indigo-500 to-purple-500',
        green: 'from-emerald-500 to-teal-400',
        blue: 'from-blue-500 to-cyan-400',
        amber: 'from-amber-500 to-yellow-400',
        pink: 'from-pink-500 to-rose-400',
    }
    const gradient = colorMap[color] || colorMap.brand

    const getScoreColor = (v) => {
        if (v >= 75) return 'text-emerald-400'
        if (v >= 50) return 'text-amber-400'
        return 'text-rose-400'
    }

    return (
        <div className="space-y-2">
            <div className="flex justify-between items-center">
                <span className="text-sm text-slate-400 font-medium">{label}</span>
                <span className={`text-sm font-bold ${getScoreColor(value)}`}>{value?.toFixed(1)}%</span>
            </div>
            <div className="progress-bar">
                <div
                    className={`h-full rounded-full bg-gradient-to-r ${gradient} transition-all duration-700`}
                    style={{ width: `${Math.min(100, value || 0)}%` }}
                />
            </div>
        </div>
    )
}

export default function ScoreBreakdown({ scores, className = '' }) {
    if (!scores) return null

    const items = [
        { label: 'Semantic Match', key: 'semantic_score', color: 'brand' },
        { label: 'Skill Overlap', key: 'skill_overlap', color: 'green' },
        { label: 'Experience Match', key: 'experience_score', color: 'blue' },
        { label: 'Location Match', key: 'location_score', color: 'amber' },
        { label: 'Salary Compatibility', key: 'salary_score', color: 'pink' },
    ]

    const scoreVal = scores.final_score
    const ringColor = scoreVal >= 75
        ? '#10b981'
        : scoreVal >= 50
            ? '#f59e0b'
            : '#ef4444'

    return (
        <div className={`glass-card p-6 ${className}`}>
            {/* Final Score Ring */}
            <div className="flex items-center gap-6 mb-6">
                <div className="relative flex items-center justify-center" style={{ width: 80, height: 80 }}>
                    <svg viewBox="0 0 80 80" className="absolute inset-0 w-full h-full -rotate-90">
                        <circle cx="40" cy="40" r="34" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="6" />
                        <circle
                            cx="40" cy="40" r="34"
                            fill="none"
                            stroke={ringColor}
                            strokeWidth="6"
                            strokeLinecap="round"
                            strokeDasharray={`${2 * Math.PI * 34}`}
                            strokeDashoffset={`${2 * Math.PI * 34 * (1 - (scoreVal || 0) / 100)}`}
                            style={{ transition: 'stroke-dashoffset 1s ease-out' }}
                        />
                    </svg>
                    <span className="text-xl font-display font-bold" style={{ color: ringColor }}>
                        {scoreVal?.toFixed(0)}
                    </span>
                </div>
                <div>
                    <p className="text-lg font-display font-bold text-white">AI Match Score</p>
                    <p className="text-sm text-slate-400">Explainable score breakdown</p>
                </div>
            </div>

            {/* Score Breakdown Bars */}
            <div className="space-y-4">
                {items.map(({ label, key, color }) => (
                    <ScoreBar key={key} label={label} value={scores[key]} color={color} />
                ))}
            </div>

            {/* Weights note */}
            <div className="mt-4 pt-4 border-t border-white/5">
                <p className="text-xs text-slate-500">
                    Weights: Semantic 40% · Skills 20% · Exp 15% · Location 15% · Salary 10%
                </p>
            </div>
        </div>
    )
}
