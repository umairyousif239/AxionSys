import React, { useState } from 'react'
import PropTypes from 'prop-types'

export default function IngestStep({ onIngested }) {
    const [repoPath, setRepoPath] = useState('')
    const [githubUrl, setGithubUrl] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [inputMode, setInputMode] = useState('local')

    const handleIngest = async () => {
        if (!repoPath && !githubUrl) {
        setError('Provide a repository path or GitHub URL.')
        return
        }

        setLoading(true)
        setError('')

        try {
        const res = await fetch('/ingest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
            repo_path: inputMode === 'local' ? repoPath : '',
            github_url: inputMode === 'github' ? githubUrl : '',
            })
        })

        const data = await res.json()

        if (!res.ok) {
            setError(data.detail || 'Ingestion failed.')
            return
        }

        onIngested(data)

        } catch (e) {
        setError(`Could not connect to AxionSys API. Is the server running? ${e.message}`)
        } finally {
        setLoading(false)
        }
    }

    return (
        <div className="fade-in" style={{ maxWidth: '640px', margin: '0 auto', width: '100%' }}>

        {/* Title */}
        <div style={{ marginBottom: '48px' }}>
            <div style={{
            fontSize: '11px',
            color: 'var(--accent-amber)',
            letterSpacing: '0.15em',
            marginBottom: '12px'
            }}>
            STEP 01 // REPOSITORY INGESTION
            </div>
            <h1 style={{
            fontFamily: 'var(--font-display)',
            fontWeight: 800,
            fontSize: '36px',
            lineHeight: 1.1,
            color: 'var(--text-primary)',
            marginBottom: '12px'
            }}>
            Point me at<br />your codebase.
            </h1>
            <p style={{
            fontSize: '13px',
            color: 'var(--text-secondary)',
            lineHeight: 1.6,
            maxWidth: '480px'
            }}>
            AxionSys will index your repository using hybrid BM25 + vector search.
            Provide a local path or a GitHub URL.
            </p>
        </div>

        {/* Mode toggle */}
        <div style={{
            display: 'flex',
            marginBottom: '24px',
            border: '1px solid var(--bg-border)',
            borderRadius: '4px',
            width: 'fit-content',
            overflow: 'hidden'
        }}>
            {['local', 'github'].map(mode => (
            <button
                key={mode}
                onClick={() => { setInputMode(mode); setError('') }}
                style={{
                padding: '8px 20px',
                fontSize: '11px',
                letterSpacing: '0.1em',
                fontFamily: 'var(--font-mono)',
                border: 'none',
                cursor: 'pointer',
                background: inputMode === mode ? 'var(--accent-amber)' : 'transparent',
                color: inputMode === mode ? '#000' : 'var(--text-secondary)',
                fontWeight: inputMode === mode ? 700 : 400,
                transition: 'all 0.2s ease',
                }}
            >
                {mode === 'local' ? 'LOCAL PATH' : 'GITHUB URL'}
            </button>
            ))}
        </div>

        {/* Input */}
        <div style={{ marginBottom: '32px' }}>
            <label style={{
            display: 'block',
            fontSize: '11px',
            letterSpacing: '0.1em',
            color: 'var(--text-secondary)',
            marginBottom: '8px'
            }}>
            {inputMode === 'local' ? 'REPOSITORY PATH' : 'GITHUB URL'}
            </label>
            <input
            type="text"
            value={inputMode === 'local' ? repoPath : githubUrl}
            onChange={e => inputMode === 'local' ? setRepoPath(e.target.value) : setGithubUrl(e.target.value)}
            placeholder={inputMode === 'local' ? 'data/repos/my_project' : 'https://github.com/user/repo'}
            onKeyDown={e => e.key === 'Enter' && handleIngest()}
            style={{
                width: '100%',
                maxWidth: '560px',
                padding: '12px 16px',
                background: 'var(--bg-elevated)',
                border: `1px solid ${error ? 'var(--accent-red)' : 'var(--bg-border)'}`,
                borderRadius: '4px',
                color: 'var(--text-primary)',
                fontFamily: 'var(--font-mono)',
                fontSize: '13px',
                outline: 'none',
                transition: 'border-color 0.2s ease',
            }}
            onFocus={e => e.target.style.borderColor = 'var(--accent-amber)'}
            onBlur={e => e.target.style.borderColor = error ? 'var(--accent-red)' : 'var(--bg-border)'}
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
            maxWidth: '560px'
            }}>
            ✗ {error}
            </div>
        )}

        {/* Submit button */}
        <button
            onClick={handleIngest}
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
            {loading ? 'INDEXING REPOSITORY...' : 'INGEST REPOSITORY →'}
        </button>

        {/* Pipeline info */}
        <div style={{
            marginTop: '48px',
            padding: '20px',
            background: 'var(--bg-secondary)',
            border: '1px solid var(--bg-border)',
            borderRadius: '4px',
            maxWidth: '560px'
        }}>
            <div style={{
            fontSize: '10px',
            letterSpacing: '0.12em',
            color: 'var(--text-secondary)',
            marginBottom: '12px'
            }}>
            PIPELINE // WHAT HAPPENS ON INGEST
            </div>
            {[
            ['01', 'Load repository files'],
            ['02', 'Chunk code into semantic segments'],
            ['03', 'Generate embeddings via Sentence Transformers'],
            ['04', 'Build FAISS vector index'],
            ['05', 'Build BM25 keyword index'],
            ].map(([num, label]) => (
            <div key={num} style={{
                display: 'flex',
                gap: '12px',
                alignItems: 'center',
                padding: '6px 0',
                borderBottom: '1px solid var(--bg-border)',
            }}>
                <span style={{ fontSize: '10px', color: 'var(--accent-amber)', minWidth: '20px' }}>{num}</span>
                <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{label}</span>
            </div>
            ))}
        </div>

        </div>
    )
}

IngestStep.propTypes = {
    onIngested: PropTypes.func.isRequired
}
