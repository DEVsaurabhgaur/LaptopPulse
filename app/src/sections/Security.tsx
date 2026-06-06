import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const securityCards = [
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      </svg>
    ),
    title: 'AES-256-GCM Encryption',
    body: 'All local log files and configuration data are encrypted at rest using hardware-accelerated AES-256-GCM. Machine-derived keys mean data is bound to the host — unreadable if stolen.',
  },
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
        <path d="M7 11V7a5 5 0 0 1 10 0v4" />
      </svg>
    ),
    title: 'Zero-Telemetry Design',
    body: 'No analytics, no crash reports, no data leaves the machine. API keys are zeroised from memory immediately after use. Privacy is the architecture, not a setting.',
  },
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4" />
      </svg>
    ),
    title: 'Supply Chain Integrity',
    body: 'Executable is signed with a code-signing certificate. SHA-256 hashes are published with every release. HMAC signatures on log entries prevent tampering.',
  },
]

const threatModel = [
  { threat: 'Malware reading logs', defense: 'Encrypted at rest' },
  { threat: 'API key theft', defense: 'Memory zeroisation' },
  { threat: 'Tampered executable', defense: 'Code signing + SHA-256' },
  { threat: 'Log injection', defense: 'HMAC per entry' },
]

export default function Security() {
  const sectionRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.utils.toArray<HTMLElement>('.security-animate').forEach((el, i) => {
        gsap.from(el, {
          opacity: 0,
          y: 40,
          duration: 0.8,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: el,
            start: 'top 80%',
            toggleActions: 'play none none none',
          },
          delay: i * 0.1,
        })
      })
    }, sectionRef)

    return () => ctx.revert()
  }, [])

  return (
    <section
      ref={sectionRef}
      id="security"
      style={{
        backgroundColor: 'var(--bg-base)',
        paddingTop: 'var(--space-xl)',
        paddingBottom: 'var(--space-xl)',
      }}
    >
      <div className="container-main">
        {/* Section Header */}
        <div className="security-animate" style={{ marginBottom: 'var(--space-lg)' }}>
          <span
            className="font-mono uppercase block"
            style={{
              fontSize: '12px',
              color: 'var(--text-muted)',
              letterSpacing: '0.15em',
            }}
          >
            Security Model
          </span>
          <h2
            className="font-heading"
            style={{
              fontSize: 'clamp(32px, 5vw, 64px)',
              fontWeight: 400,
              color: 'var(--text-primary)',
              marginTop: '8px',
            }}
          >
            Built Safe, Not Bolted On
          </h2>
        </div>

        {/* Two-Column Layout */}
        <div
          className="grid grid-cols-1 md:grid-cols-2"
          style={{ gap: 'var(--space-lg)' }}
        >
          {/* Left Column - Security Cards */}
          <div className="flex flex-col" style={{ gap: 'var(--space-sm)' }}>
            {securityCards.map((card, i) => (
              <div
                key={i}
                className="security-animate"
                style={{
                  backgroundColor: 'var(--bg-surface)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: 'var(--space-md)',
                }}
              >
                <div style={{ color: 'var(--accent-cyan)' }}>{card.icon}</div>
                <h3
                  style={{
                    fontFamily: 'var(--font-body)',
                    fontSize: '16px',
                    fontWeight: 600,
                    color: 'var(--text-primary)',
                    marginTop: '12px',
                  }}
                >
                  {card.title}
                </h3>
                <p
                  style={{
                    fontFamily: 'var(--font-body)',
                    fontSize: '16px',
                    color: 'var(--text-secondary)',
                    marginTop: '8px',
                    lineHeight: 1.6,
                  }}
                >
                  {card.body}
                </p>
              </div>
            ))}
          </div>

          {/* Right Column - Threat Model */}
          <div className="security-animate">
            <div
              className="glass-card"
              style={{ padding: 'var(--space-lg)', height: '100%' }}
            >
              <h3
                className="font-mono uppercase"
                style={{
                  fontSize: '14px',
                  color: 'var(--text-muted)',
                  letterSpacing: '0.1em',
                }}
              >
                Threat Model
              </h3>

              <div style={{ marginTop: 'var(--space-md)' }}>
                {threatModel.map((row, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between"
                    style={{
                      borderBottom: '1px solid var(--border-subtle)',
                      padding: '12px 0',
                    }}
                  >
                    <span
                      style={{
                        fontFamily: 'var(--font-body)',
                        fontSize: '16px',
                        color: 'var(--text-secondary)',
                      }}
                    >
                      {row.threat}
                    </span>
                    <span
                      className="font-mono"
                      style={{
                        fontSize: '13px',
                        color: 'var(--accent-green)',
                        fontWeight: 500,
                      }}
                    >
                      {row.defense}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
