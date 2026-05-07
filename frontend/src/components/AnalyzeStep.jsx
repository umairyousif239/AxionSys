import React, { useState } from 'react'
import PropTypes from 'prop-types'

export default function AnalyzeStep({ session, onAnalyzed, onBack }) {
    const [logText, setLogText] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [traceSteps, setTraceSteps] = useState([])

    const addTrace = (msg) => {
        setTraceSteps(prev => [...prev, { msg, time: new Date().toLocaleTimeString() }])
    }

    const handleAnalyze = async () => {
        if (!logText.trim()) {
        setError('Paste an error log or traceback.')
        return
        }

        setLoading(true)
        setError('')
        setTraceSteps([])

        addTrace('Parsing log input...')

        try {
        setTimeout(() => addTrace('Extracting queries from error...'), 600)
        setTimeout(() => addTrace('Running hybrid retrieval (BM25 + FAISS)...'), 1200)
        setTimeout(() => addTrace('Reranking results with Qwen 3.5 9B...'), 2000)
        setTimeout(() => addTrace('Generating root cause analysis...'), 3000)
        setTimeout(() => addTrace('Generating fix with unified diff...'), 4500)

        const res = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
            session_id: session.session_id,
            log_text: logText,
            })
        })

        const data = await res.json()

        if (!res.ok) {
            setError(data.detail || 'Analysis failed.')
            return
        }

        addTrace('Analysis complete.')
        setTimeout(() => onAnalyzed(data), 600)

        } catch (e) {
        setError(`Could not connect to AxionSys API. ${e.message}`)
        } finally {
        setLoading(false)
        }
    }

    const borderColor = error ? 'var(--accent-red)' : 'var(--bg-border)'

    return (
        <div className="fade-in" style={{ maxWidth: '640px', margin: '0 auto', width: '100%' }}>

        <div style={{ marginBottom: '32px' }}>
            <div style={{
            fontSize: '11px',
            color: 'var(--accent-amber)',
            letterSpacing: '0.15em',
            marginBottom: '12px'
            }}>
            STEP 02 {'// LOG ANALYSIS'}
            </div>
            <h1 style={{
            fontFamily: 'var(--font-display)',
            fontWeight: 800,
            fontSize: '36px',
            lineHeight: 1.1,
            color: 'var(--text-primary)',
            marginBottom: '12px'
            }}>
            Show me<br />the error.
            </h1>
            <p style={{
            fontSize: '13px',
            color: 'var(--text-secondary)',
            lineHeight: 1.6,
            maxWidth: '480px'
            }}>
            Paste a Python traceback, log file output, or free-form error description.
            AxionSys will extract the root cause and generate a fix.
            </p>
        </div>

        {/* Session info */}
        <div style={{
            display: 'flex',
            gap: '24px',
            marginBottom: '28px',
            padding: '12px 16px',
            background: 'var(--bg-elevated)',
            border: '1px solid var(--bg-border)',
            borderRadius: '4px',
            maxWidth: '640px'
        }}>
            <div>
            <div style={{ fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.1em', marginBottom: '4px' }}>REPO</div>
            <div style={{ fontSize: '12px', color: 'var(--accent-green)' }}>{session.repo_path}</div>
            </div>
            <div style={{ borderLeft: '1px solid var(--bg-border)', paddingLeft: '24px' }}>
            <div style={{ fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.1em', marginBottom: '4px' }}>CHUNKS INDEXED</div>
            <div style={{ fontSize: '12px', color: 'var(--accent-amber)' }}>{session.chunk_count}</div>
            </div>
            <div style={{ borderLeft: '1px solid var(--bg-border)', paddingLeft: '24px' }}>
            <div style={{ fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.1em', marginBottom: '4px' }}>SESSION</div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{session.session_id.slice(0, 12)}...</div>
            </div>
        </div>

        {/* Log input */}
        <div style={{ marginBottom: '24px' }}>
            <label
            htmlFor="log-input"
            style={{
                display: 'block',
                fontSize: '11px',
                letterSpacing: '0.1em',
                color: 'var(--text-secondary)',
                marginBottom: '8px'
            }}
            >
            ERROR LOG / TRACEBACK
            </label>
            <textarea
            value={logText}
            onChange={e => setLogText(e.target.value)}
            placeholder={`Traceback (most recent call last):\n  File "api/routes.py", line 12, in user_route\n    return get_user_data()\nAttributeError: 'NoneType' object has no attribute 'cursor'`}
            rows={10}
            style={{
                width: '100%',
                maxWidth: '640px',
                padding: '14px 16px',
                background: 'var(--bg-elevated)',
                border: `1px solid ${borderColor}`,
                borderRadius: '4px',
                color: 'var(--text-primary)',
                fontFamily: 'var(--font-mono)',
                fontSize: '12px',
                lineHeight: 1.6,
                outline: 'none',
                resize: 'vertical',
                transition: 'border-color 0.2s ease',
            }}
            onFocus={e => { e.target.style.borderColor = 'var(--accent-amber)' }}
            onBlur={e => { e.target.style.borderColor = borderColor }}
            />
        </div>

        {/* Error */}
        {error && (
            <div style={{
            marginBottom: '24px',
            padding: '10px 14px',
            background: 'rgba(239,68,68,0.1)',
            border: '1px solid rgba(239,68,68,0.3)',
            borderRadius: '4px',
            fontSize: '12px',
            color: 'var(--accent-red)',
            maxWidth: '640px'
            }}>
            ✗ {error}
            </div>
        )}

        {/* Execution trace */}
        {traceSteps.length > 0 && (
            <div style={{
            marginBottom: '24px',
            padding: '16px',
            background: 'var(--bg-secondary)',
            border: '1px solid var(--bg-border)',
            borderRadius: '4px',
            maxWidth: '640px'
            }}>
            <div style={{
                fontSize: '10px',
                letterSpacing: '0.12em',
                color: 'var(--text-secondary)',
                marginBottom: '12px'
            }}>
                EXECUTION TRACE
            </div>
            {traceSteps.map((step) => (
                <div key={`${step.time}-${step.msg}`} className="slide-in" style={{
                display: 'flex',
                gap: '12px',
                alignItems: 'center',
                padding: '5px 0',
                }}>
                <span style={{ fontSize: '10px', color: 'var(--accent-green)', minWidth: '70px' }}>{step.time}</span>
                <span style={{ fontSize: '10px', color: 'var(--bg-border)' }}>▶</span>
                <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{step.msg}</span>
                </div>
            ))}
            {loading && (
                <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '5px 0',
                marginTop: '4px'
                }}>
                <div style={{
                    width: '8px', height: '8px',
                    border: '1px solid var(--text-muted)',
                    borderTopColor: 'var(--accent-amber)',
                    borderRadius: '50%',
                    animation: 'spin 0.8s linear infinite',
                    marginLeft: '82px'
                }} />
                <span style={{ fontSize: '12px', color: 'var(--text-muted)', animation: 'pulse 1.5s infinite' }}>
                    processing...
                </span>
                </div>
            )}
            </div>
        )}

        {/* Buttons */}
        <div style={{ display: 'flex', gap: '12px' }}>
            <button
            onClick={onBack}
            disabled={loading}
            style={{
                padding: '12px 20px',
                background: 'transparent',
                color: 'var(--text-secondary)',
                border: '1px solid var(--bg-border)',
                borderRadius: '4px',
                fontFamily: 'var(--font-mono)',
                fontSize: '12px',
                letterSpacing: '0.1em',
                cursor: loading ? 'not-allowed' : 'pointer',
            }}
            >
            ← BACK
            </button>

            <button
            onClick={handleAnalyze}
            disabled={loading}
            style={{
                padding: '12px 28px',
                background: loading ? 'var(--bg-elevated)' : 'var(--accent-amber)',
                color: loading ? 'var(--text-secondary)' : '#000',
                border: 'none',
                borderRadius: '4px',
                fontFamily: 'var(--font-mono)',
                fontSize: '12px',
                fontWeight: 700,
                letterSpacing: '0.1em',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
            }}
            >
            {loading && (
                <div style={{
                width: '12px', height: '12px',
                border: '2px solid var(--text-muted)',
                borderTopColor: 'var(--accent-amber)',
                borderRadius: '50%',
                animation: 'spin 0.8s linear infinite'
                }} />
            )}
            {loading ? 'ANALYZING...' : 'ANALYZE →'}
            </button>
        </div>

        </div>
    )
}

AnalyzeStep.propTypes = {
    session: PropTypes.shape({
        session_id: PropTypes.string.isRequired,
        repo_path: PropTypes.string.isRequired,
        chunk_count: PropTypes.number.isRequired,
    }).isRequired,
    onAnalyzed: PropTypes.func.isRequired,
    onBack: PropTypes.func.isRequired,
}