import React, { useState } from 'react'
import IngestStep from './components/IngestStep'
import AnalyzeStep from './components/AnalyzeStep'
import ResultsStep from './components/ResultsStep'

const STEPS = ['INGEST', 'ANALYZE', 'RESULTS']

function getStepBorderColor(i, step) {
    if (i < step) return 'var(--accent-green)'
    if (i === step) return 'var(--accent-amber)'
    return 'var(--bg-border)'
}

function getStepTextColor(i, step) {
    if (i < step) return 'var(--accent-green)'
    if (i === step) return 'var(--accent-amber)'
    return 'var(--text-muted)'
}

export default function App() {
    const [step, setStep] = useState(0)
    const [session, setSession] = useState(null)
    const [results, setResults] = useState(null)

    const handleIngested = (sessionData) => {
        setSession(sessionData)
        setStep(1)
    }

    const handleAnalyzed = (analysisResults) => {
        setResults(analysisResults)
        setStep(2)
    }

    const handleReset = () => {
        setStep(0)
        setSession(null)
        setResults(null)
    }

    return (
        <div style={{ 
            minHeight: '100vh', 
            display: 'flex', 
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%'
        }}>

        {/* Header */}
        <header style={{
            borderBottom: '1px solid var(--bg-border)',
            padding: '16px 32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: 'var(--bg-secondary)',
            width: '100%',
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
                width: '8px', height: '8px',
                borderRadius: '50%',
                background: 'var(--accent-green)',
                boxShadow: '0 0 8px var(--accent-green)',
                animation: 'pulse 2s infinite'
            }} />
            <span style={{
                fontFamily: 'var(--font-display)',
                fontWeight: 800,
                fontSize: '18px',
                letterSpacing: '0.05em',
                color: 'var(--text-primary)'
            }}>
                AXIONSYS
            </span>
            <span style={{
                fontSize: '10px',
                color: 'var(--text-secondary)',
                letterSpacing: '0.1em',
                marginLeft: '4px'
            }}>
                v1.0 // LOCAL AI DEBUGGER
            </span>
            </div>

            {/* Step indicator */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {STEPS.map((s, i) => (
                <div key={s} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{
                    display: 'flex', alignItems: 'center', gap: '6px',
                    opacity: i <= step ? 1 : 0.3,
                    transition: 'opacity 0.3s ease'
                }}>
                    <div style={{
                        width: '20px', height: '20px',
                        border: `1px solid ${getStepBorderColor(i, step)}`,
                        borderRadius: '2px',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: '10px',
                        color: getStepTextColor(i, step),
                        background: i < step ? 'rgba(16,185,129,0.1)' : 'transparent',
                    }}>
                    {i < step ? '✓' : i + 1}
                    </div>
                    <span style={{
                        fontSize: '10px',
                        letterSpacing: '0.1em',
                        color: i === step ? 'var(--accent-amber)' : 'var(--text-secondary)'
                    }}>
                    {s}
                    </span>
                </div>
                {i < STEPS.length - 1 && (
                    <span style={{ color: 'var(--text-muted)', fontSize: '10px' }}>—</span>
                )}
                </div>
            ))}
            </div>

            {/* AMD badge */}
            <div style={{
                fontSize: '10px',
                color: 'var(--text-secondary)',
                letterSpacing: '0.08em',
                display: 'flex', alignItems: 'center', gap: '6px'
            }}>
            <div style={{
                width: '6px', height: '6px',
                borderRadius: '50%',
                background: 'var(--accent-red)',
            }} />
            LOCAL INFERENCE
            </div>
        </header>

        {/* Main content */}
        <main style={{
            flex: 1,
            padding: '48px 32px',
            maxWidth: '900px',
            width: '100%',
            margin: '0 auto',
            display: 'flex',
            flexDirection: 'column',
        }}>
            {step === 0 && (
            <IngestStep onIngested={handleIngested} />
            )}
            {step === 1 && (
            <AnalyzeStep session={session} onAnalyzed={handleAnalyzed} onBack={() => setStep(0)} />
            )}
            {step === 2 && (
            <ResultsStep results={results} session={session} onReset={handleReset} />
            )}
        </main>

        {/* Footer */}
        <footer style={{
            borderTop: '1px solid var(--bg-border)',
            padding: '12px 32px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            background: 'var(--bg-secondary)',
            width: '100%',
        }}>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)', letterSpacing: '0.08em' }}>
            AXIONSYS // NO CLOUD // NO DATA LEAVES YOUR MACHINE
            </span>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)', letterSpacing: '0.08em' }}>
            QWEN 3.5 9B + MISTRAL 7B // OLLAMA RUNTIME
            </span>
        </footer>

        </div>
    )
}