import React, { useState } from 'react'
import PropTypes from 'prop-types'

function getLineColor(line) {
    if (line.startsWith('+') && !line.startsWith('+++')) return 'var(--accent-green)'
    if (line.startsWith('-') && !line.startsWith('---')) return 'var(--accent-red)'
    if (line.startsWith('@@') || line.startsWith('---') || line.startsWith('+++')) return 'var(--accent-blue)'
    return 'var(--text-secondary)'
}

function getLineBackground(line) {
    if (line.startsWith('+') && !line.startsWith('+++')) return 'rgba(16,185,129,0.08)'
    if (line.startsWith('-') && !line.startsWith('---')) return 'rgba(239,68,68,0.08)'
    return 'transparent'
}

function getConfidenceColor(value) {
    if (value >= 0.9) return 'var(--accent-green)'
    if (value >= 0.7) return 'var(--accent-amber)'
    return 'var(--accent-red)'
}

function ConfidenceBadge({ value }) {
    const color = getConfidenceColor(value)
    return (
        <span style={{
        padding: '2px 8px',
        border: `1px solid ${color}`,
        borderRadius: '2px',
        fontSize: '10px',
        color,
        letterSpacing: '0.08em',
        background: `${color}15`
        }}>
        {Math.round(value * 100)}% CONFIDENCE
        </span>
    )
}

ConfidenceBadge.propTypes = {
    value: PropTypes.number.isRequired
}

function ScoreBar({ value, color }) {
    return (
        <div style={{
        height: '3px',
        background: 'var(--bg-border)',
        borderRadius: '2px',
        overflow: 'hidden',
        width: '60px'
        }}>
        <div style={{
            height: '100%',
            width: `${value * 100}%`,
            background: color,
            borderRadius: '2px',
            transition: 'width 0.6s ease'
        }} />
        </div>
    )
}

ScoreBar.defaultProps = {
    color: 'var(--accent-amber)'
}

ScoreBar.propTypes = {
    value: PropTypes.number.isRequired,
    color: PropTypes.string
}

function DiffView({ diff }) {
    if (!diff) return null
    const lines = diff.split('\n')
    return (
        <div style={{
        background: 'var(--bg-primary)',
        border: '1px solid var(--bg-border)',
        borderRadius: '4px',
        overflow: 'hidden',
        fontFamily: 'var(--font-mono)',
        fontSize: '12px',
        }}>
        <div style={{
            padding: '8px 14px',
            background: 'var(--bg-elevated)',
            borderBottom: '1px solid var(--bg-border)',
            fontSize: '10px',
            color: 'var(--text-secondary)',
            letterSpacing: '0.1em'
        }}>
            UNIFIED DIFF
        </div>
        <div style={{ padding: '12px 0', overflowX: 'auto' }}>
            {lines.map((line, i) => (
            <div key={`line-${i}-${line.slice(0, 10)}`} style={{
                padding: '2px 14px',
                background: getLineBackground(line),
                color: getLineColor(line),
                whiteSpace: 'pre',
            }}>
                {line}
            </div>
            ))}
        </div>
        </div>
    )
}

DiffView.propTypes = {
    diff: PropTypes.string
}

DiffView.defaultProps = {
    diff: null
}

function ResultCard({ result, index }) {
    const [activeTab, setActiveTab] = useState('root_cause')
    const rc = result.root_cause
    const fix = result.fix
    const tabs = ['root_cause', 'chain', 'fix', 'files', 'trace']

    return (
        <div className="fade-in" style={{
        border: '1px solid var(--bg-border)',
        borderRadius: '4px',
        overflow: 'hidden',
        marginBottom: '24px',
        animationDelay: `${index * 0.1}s`
        }}>

        {/* Card header */}
        <div style={{
            padding: '16px 20px',
            background: 'var(--bg-elevated)',
            borderBottom: '1px solid var(--bg-border)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            gap: '12px'
        }}>
            <div style={{ flex: 1 }}>
            <div style={{
                fontSize: '10px',
                color: 'var(--text-secondary)',
                letterSpacing: '0.1em',
                marginBottom: '6px'
            }}>
                {result.type.toUpperCase()} {'// ERROR'} {index + 1}
            </div>
            <div style={{
                fontSize: '13px',
                color: 'var(--accent-red)',
                fontFamily: 'var(--font-mono)',
                wordBreak: 'break-all'
            }}>
                {result.error}
            </div>
            </div>
            <ConfidenceBadge value={rc.confidence} />
        </div>

        {/* Tabs */}
        <div style={{
            display: 'flex',
            borderBottom: '1px solid var(--bg-border)',
            background: 'var(--bg-secondary)'
        }}>
            {tabs.map(tab => (
            <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                style={{
                padding: '10px 16px',
                fontSize: '10px',
                letterSpacing: '0.1em',
                fontFamily: 'var(--font-mono)',
                border: 'none',
                borderBottom: `2px solid ${activeTab === tab ? 'var(--accent-amber)' : 'transparent'}`,
                cursor: 'pointer',
                background: 'transparent',
                color: activeTab === tab ? 'var(--accent-amber)' : 'var(--text-secondary)',
                transition: 'all 0.15s ease',
                }}
            >
                {tab.replace('_', ' ').toUpperCase()}
            </button>
            ))}
        </div>

        {/* Tab content */}
        <div style={{ padding: '20px' }}>

            {activeTab === 'root_cause' && (
            <div className="fade-in">
                <div style={{
                padding: '14px 16px',
                background: 'rgba(239,68,68,0.06)',
                border: '1px solid rgba(239,68,68,0.2)',
                borderRadius: '4px',
                marginBottom: '20px'
                }}>
                <div style={{ fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.1em', marginBottom: '8px' }}>ROOT CAUSE</div>
                <div style={{ fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.6 }}>{rc.root_cause}</div>
                </div>

                <div style={{ marginBottom: '20px' }}>
                <div style={{ fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.1em', marginBottom: '10px' }}>REASONING CHAIN</div>
                {rc.reasoning.split('\n').filter(Boolean).map((line, i) => (
                    <div key={line} style={{
                    display: 'flex',
                    gap: '10px',
                    padding: '6px 0',
                    borderBottom: '1px solid var(--bg-border)'
                    }}>
                    <span style={{ color: 'var(--accent-amber)', fontSize: '11px', minWidth: '16px' }}>▶</span>
                    <span style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{line.replace(/^\d+\.\s*/, '')}</span>
                    </div>
                ))}
                </div>

                <div>
                <div style={{ fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.1em', marginBottom: '10px' }}>AFFECTED FILES</div>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                    {rc.affected_files.map(f => (
                    <span key={f} style={{
                        padding: '4px 10px',
                        background: 'rgba(245,158,11,0.1)',
                        border: '1px solid rgba(245,158,11,0.3)',
                        borderRadius: '2px',
                        fontSize: '11px',
                        color: 'var(--accent-amber)',
                        fontFamily: 'var(--font-mono)'
                    }}>
                        {f}
                    </span>
                    ))}
                </div>
                </div>
            </div>
            )}

            {activeTab === 'chain' && (
            <div className="fade-in">
                <div style={{ fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.1em', marginBottom: '24px' }}>
                CALL CHAIN // BUG PROPAGATION PATH
                </div>

                {rc.call_chain && rc.call_chain.length > 0 ? (
                <div style={{ overflowX: 'auto', paddingBottom: '12px' }}>
                    <svg
                    viewBox={`0 0 ${rc.call_chain.length * 180 - 20} 120`}
                    style={{ width: '100%', minWidth: `${rc.call_chain.length * 180 - 20}px`, height: '120px' }}
                    xmlns="http://www.w3.org/2000/svg"
                    >
                    {rc.call_chain.map((node, i) => {
                        const x = i * 180
                        const isLast = i === rc.call_chain.length - 1

                        let boxColor, textColor, glowColor
                        if (node.status === 'bug') {
                        boxColor = '#451a03'
                        textColor = '#f59e0b'
                        glowColor = '#f59e0b'
                        } else if (node.status === 'crash') {
                        boxColor = '#450a0a'
                        textColor = '#ef4444'
                        glowColor = '#ef4444'
                        } else {
                        boxColor = '#1a1a1a'
                        textColor = '#737373'
                        glowColor = '#404040'
                        }

                        return (
                        <g key={node.file}>
                            {/* Arrow between nodes */}
                            {!isLast && (
                            <g>
                                <line
                                x1={x + 140} y1={60}
                                x2={x + 170} y2={60}
                                stroke="#2a2a2a"
                                strokeWidth="1.5"
                                />
                                <polygon
                                points={`${x + 175},56 ${x + 180},60 ${x + 175},64`}
                                fill="#2a2a2a"
                                />
                            </g>
                            )}

                            {/* Node box */}
                            <rect
                            x={x} y={30}
                            width={140} height={60}
                            rx={3}
                            fill={boxColor}
                            stroke={glowColor}
                            strokeWidth="1"
                            style={{ filter: node.status === 'ok' ? 'none' : `drop-shadow(0 0 4px ${glowColor}40)` }}
                            />

                            {/* Status badge */}
                            <rect
                            x={x + 4} y={34}
                            width={node.status.length * 7 + 8} height={14}
                            rx={2}
                            fill={`${glowColor}20`}
                            />
                            <text
                            x={x + 8} y={44}
                            fontSize="8"
                            fill={glowColor}
                            fontFamily="JetBrains Mono, monospace"
                            letterSpacing="0.05em"
                            >
                            {node.status.toUpperCase()}
                            </text>

                            {/* File name */}
                            <text
                            x={x + 70} y={62}
                            fontSize="11"
                            fill={textColor}
                            fontFamily="JetBrains Mono, monospace"
                            textAnchor="middle"
                            fontWeight={node.status === 'ok' ? '400' : '700'}
                            >
                            {node.file}
                            </text>

                            {/* Function name */}
                            <text
                            x={x + 70} y={76}
                            fontSize="9"
                            fill={`${textColor}99`}
                            fontFamily="JetBrains Mono, monospace"
                            textAnchor="middle"
                            >
                            {node.function}()
                            </text>
                        </g>
                        )
                    })}
                    </svg>

                    {/* Legend */}
                    <div style={{
                    display: 'flex',
                    gap: '20px',
                    marginTop: '20px',
                    padding: '12px 16px',
                    background: 'var(--bg-elevated)',
                    border: '1px solid var(--bg-border)',
                    borderRadius: '4px',
                    }}>
                    {[
                        ['OK', 'var(--text-secondary)', 'Passes through'],
                        ['CRASH', 'var(--accent-red)', 'Exception raised here'],
                        ['BUG', 'var(--accent-amber)', 'Root cause originates here'],
                    ].map(([label, color, desc]) => (
                        <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{
                            width: '8px', height: '8px',
                            borderRadius: '2px',
                            background: color,
                            boxShadow: label === 'OK' ? 'none' : `0 0 4px ${color}`
                        }} />
                        <span style={{ fontSize: '10px', color, letterSpacing: '0.08em' }}>{label}</span>
                        <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>— {desc}</span>
                        </div>
                    ))}
                    </div>
                </div>
                ) : (
                <div style={{
                    padding: '20px',
                    background: 'var(--bg-elevated)',
                    border: '1px solid var(--bg-border)',
                    borderRadius: '4px',
                    fontSize: '12px',
                    color: 'var(--text-secondary)'
                }}>
                    No call chain data available for this error.
                </div>
                )}
            </div>
            )}

            {activeTab === 'fix' && (
            <div className="fade-in">
                <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '16px'
                }}>
                <div style={{ fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.1em' }}>
                    FILE: <span style={{ color: 'var(--accent-amber)' }}>{fix.affected_file}</span>
                </div>
                <ConfidenceBadge value={fix.confidence} />
                </div>

                {fix.diff && <DiffView diff={fix.diff} />}

                {!fix.diff && fix.diff_warning && (
                <div style={{
                    padding: '10px 14px',
                    background: 'rgba(245,158,11,0.08)',
                    border: '1px solid rgba(245,158,11,0.2)',
                    borderRadius: '4px',
                    fontSize: '12px',
                    color: 'var(--accent-amber)',
                    marginBottom: '16px'
                }}>
                    ⚠ {fix.diff_warning}
                </div>
                )}

                <div style={{
                marginTop: '16px',
                padding: '14px 16px',
                background: 'var(--bg-elevated)',
                border: '1px solid var(--bg-border)',
                borderRadius: '4px',
                }}>
                <div style={{ fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.1em', marginBottom: '8px' }}>EXPLANATION</div>
                <div style={{ fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.6 }}>{fix.explanation}</div>
                </div>
            </div>
            )}

            {activeTab === 'files' && (
            <div className="fade-in">
                <div style={{ fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.1em', marginBottom: '16px' }}>
                TOP RETRIEVED FILES // RANKED BY FINAL SCORE
                </div>
                {result.top_files.map((f, i) => (
                <div key={f.file} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '16px',
                    padding: '10px 0',
                    borderBottom: '1px solid var(--bg-border)',
                }}>
                    <span style={{ fontSize: '10px', color: 'var(--text-muted)', minWidth: '20px' }}>#{i + 1}</span>
                    <span style={{ fontSize: '12px', color: 'var(--accent-amber)', minWidth: '140px' }}>{f.file}</span>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '10px', color: 'var(--text-muted)', minWidth: '60px' }}>FINAL</span>
                        <ScoreBar value={f.final_score} color="var(--accent-amber)" />
                        <span style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>{f.final_score}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '10px', color: 'var(--text-muted)', minWidth: '60px' }}>HYBRID</span>
                        <ScoreBar value={f.hybrid_score} color="var(--accent-blue)" />
                        <span style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>{f.hybrid_score}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '10px', color: 'var(--text-muted)', minWidth: '60px' }}>RERANK</span>
                        <ScoreBar value={f.rerank_score} color="var(--accent-green)" />
                        <span style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>{f.rerank_score}</span>
                    </div>
                    </div>
                </div>
                ))}

                {result.files_mentioned.length > 0 && (
                <div style={{ marginTop: '20px' }}>
                    <div style={{ fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.1em', marginBottom: '12px' }}>
                    FILES MENTIONED IN TRACEBACK
                    </div>
                    {result.files_mentioned.map((f, i) => (
                    <div key={`${f.file}-${f.line}`} style={{
                        display: 'flex',
                        gap: '12px',
                        padding: '6px 0',
                        borderBottom: '1px solid var(--bg-border)',
                        fontSize: '12px'
                    }}>
                        <span style={{ color: 'var(--text-muted)', minWidth: '20px' }}>{i + 1}</span>
                        <span style={{ color: 'var(--accent-amber)' }}>{f.file}</span>
                        <span style={{ color: 'var(--text-secondary)' }}>line {f.line}</span>
                        <span style={{ color: 'var(--text-muted)' }}>in {f.function}()</span>
                    </div>
                    ))}
                </div>
                )}
            </div>
            )}

            {activeTab === 'trace' && (
            <div className="fade-in">
                <div style={{ fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.1em', marginBottom: '16px' }}>
                PIPELINE EXECUTION TRACE
                </div>
                {[
                ['PARSE', `Identified error type: ${result.type}`, 'var(--accent-green)'],
                ['QUERY', `Primary: "${result.primary_query}"`, 'var(--accent-amber)'],
                ['QUERY', `Secondary: ${result.secondary_queries.join(' | ')}`, 'var(--accent-amber)'],
                ['RETRIEVE', `Top files: ${result.top_files.map(f => f.file).join(', ')}`, 'var(--accent-blue)'],
                ['RERANK', `Best match: ${result.top_files[0]?.file} (score: ${result.top_files[0]?.final_score})`, 'var(--accent-blue)'],
                ['ANALYZE', `Root cause identified — confidence: ${Math.round(rc.confidence * 100)}%`, 'var(--accent-red)'],
                ['FIX', `Patch generated for: ${fix.affected_file} — confidence: ${Math.round(fix.confidence * 100)}%`, 'var(--accent-green)'],
                ].map(([stage, detail, color], i) => (
                <div key={`trace-${stage}-${i}`} className="slide-in" style={{
                    display: 'flex',
                    gap: '12px',
                    padding: '8px 0',
                    borderBottom: '1px solid var(--bg-border)',
                    animationDelay: `${i * 0.05}s`
                }}>
                    <span style={{
                    fontSize: '10px',
                    color,
                    minWidth: '64px',
                    letterSpacing: '0.08em',
                    padding: '2px 6px',
                    border: `1px solid ${color}30`,
                    borderRadius: '2px',
                    background: `${color}10`,
                    height: 'fit-content'
                    }}>
                    {stage}
                    </span>
                    <span style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{detail}</span>
                </div>
                ))}
            </div>
            )}

        </div>
        </div>
    )
}

ResultCard.propTypes = {
    result: PropTypes.object.isRequired,
    index: PropTypes.number.isRequired
}

export default function ResultsStep({ results, session, onReset }) {
    const errorLabel = results.error_count === 1 ? 'error' : 'errors'
    return (
        <div className="fade-in" style={{ maxWidth: '780px', margin: '0 auto', width: '100%' }}>

        <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            marginBottom: '32px'
        }}>
            <div>
            <div style={{
                fontSize: '11px',
                color: 'var(--accent-green)',
                letterSpacing: '0.15em',
                marginBottom: '12px'
            }}>
                STEP 03 // ANALYSIS COMPLETE
            </div>
            <h1 style={{
                fontFamily: 'var(--font-display)',
                fontWeight: 800,
                fontSize: '36px',
                lineHeight: 1.1,
                color: 'var(--text-primary)',
                marginBottom: '8px'
            }}>
                {results.error_count} {errorLabel} found.
            </h1>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                Repo: <span style={{ color: 'var(--accent-amber)' }}>{session.repo_path}</span>
            </p>
            </div>

            <button
            onClick={onReset}
            style={{
                padding: '10px 18px',
                background: 'transparent',
                color: 'var(--text-secondary)',
                border: '1px solid var(--bg-border)',
                borderRadius: '4px',
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                letterSpacing: '0.1em',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
            }}
            onMouseEnter={e => {
                e.target.style.borderColor = 'var(--accent-amber)'
                e.target.style.color = 'var(--accent-amber)'
            }}
            onMouseLeave={e => {
                e.target.style.borderColor = 'var(--bg-border)'
                e.target.style.color = 'var(--text-secondary)'
            }}
            >
            ↺ NEW ANALYSIS
            </button>
        </div>

        {results.results.map((result, i) => (
            <ResultCard key={`result-${result.error}-${i}`} result={result} index={i} />
        ))}

        </div>
    )
}

ResultsStep.propTypes = {
    results: PropTypes.object.isRequired,
    session: PropTypes.object.isRequired,
    onReset: PropTypes.func.isRequired
}