import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import CyanCircuitry from './CyanCircuitry'

gsap.registerPlugin(ScrollTrigger)

export default function ProjectOverview() {
  const sectionRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.utils.toArray<HTMLElement>('.project-animate').forEach((el, i) => {
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
      id="overview"
      style={{
        backgroundColor: 'var(--bg-base)',
        paddingTop: 'var(--space-xl)',
        paddingBottom: 'var(--space-xl)',
      }}
    >
      <div className="container-main">
        {/* Section Header */}
        <div className="project-animate">
          <span
            className="font-mono uppercase block"
            style={{
              fontSize: '12px',
              color: 'var(--text-muted)',
              letterSpacing: '0.15em',
            }}
          >
            Project Overview
          </span>
          <h2
            className="font-heading"
            style={{
              fontSize: 'clamp(32px, 5vw, 64px)',
              fontWeight: 400,
              color: 'var(--text-primary)',
              marginTop: '8px',
              marginBottom: 'var(--space-lg)',
            }}
          >
            Silent. Precise. Always On.
          </h2>
        </div>

        {/* Two-Column Layout */}
        <div
          className="grid grid-cols-1 md:grid-cols-2"
          style={{ gap: 'var(--space-lg)' }}
        >
          {/* Left Column */}
          <div className="project-animate">
            <p
              style={{
                fontFamily: 'var(--font-body)',
                fontSize: '18px',
                color: 'var(--text-secondary)',
                lineHeight: 1.7,
              }}
            >
              LaptopPulse is a lightweight background service that monitors laptop hardware health 24/7. 
              It collects temperature, fan speed, and performance metrics every 60 seconds, stores them 
              in compressed local logs, and uses a rule-based anomaly detector to catch degradation 
              trends 30–60 days before failure. When an anomaly is detected, an AI engine generates a 
              plain-language service report — no jargon, just action.
            </p>

            {/* Stats Row */}
            <div className="flex items-center" style={{ marginTop: 'var(--space-md)' }}>
              {[
                { value: '< 0.3%', label: 'CPU Usage' },
                { value: '4 Layers', label: 'Architecture' },
                { value: '100%', label: 'Local Data' },
              ].map((stat, i) => (
                <div key={i} className="flex items-center">
                  <div>
                    <div
                      className="font-mono"
                      style={{ fontSize: '24px', color: 'var(--accent-cyan)' }}
                    >
                      {stat.value}
                    </div>
                    <div
                      className="font-mono uppercase"
                      style={{ fontSize: '11px', color: 'var(--text-muted)' }}
                    >
                      {stat.label}
                    </div>
                  </div>
                  {i < 2 && (
                    <div
                      style={{
                        width: '1px',
                        height: '40px',
                        backgroundColor: 'var(--border-subtle)',
                        margin: '0 24px',
                      }}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Right Column - Mini Dashboard */}
          <div className="project-animate">
            <div
              className="glass-card overflow-hidden"
              style={{ padding: 'var(--space-md)' }}
            >
              {/* LIVE MONITOR Label */}
              <span
                className="font-mono uppercase animate-pulse-label"
                style={{
                  fontSize: '10px',
                  color: 'var(--accent-cyan)',
                  letterSpacing: '0.1em',
                }}
              >
                Live Monitor
              </span>

              {/* Mini Dashboard Canvas */}
              <div
                className="relative overflow-hidden"
                style={{
                  height: '300px',
                  borderRadius: '8px',
                  marginTop: '8px',
                  background: 'var(--bg-surface)',
                }}
              >
                <CyanCircuitry className="absolute inset-0" isDashboard />
              </div>

              {/* Metric Ticker */}
              <div
                className="overflow-hidden"
                style={{
                  height: '40px',
                  marginTop: '8px',
                  backgroundColor: 'var(--bg-base)',
                  borderRadius: '4px',
                  display: 'flex',
                  alignItems: 'center',
                }}
              >
                <div className="animate-ticker whitespace-nowrap font-mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  <span>CPU_TEMP</span>
                  <span style={{ color: 'var(--accent-cyan)', margin: '0 8px' }}>•</span>
                  <span>GPU_TEMP</span>
                  <span style={{ color: 'var(--accent-cyan)', margin: '0 8px' }}>•</span>
                  <span>FAN_RPM</span>
                  <span style={{ color: 'var(--accent-cyan)', margin: '0 8px' }}>•</span>
                  <span>CPU_LOAD</span>
                  <span style={{ color: 'var(--accent-cyan)', margin: '0 8px' }}>•</span>
                  <span>CPU_TEMP</span>
                  <span style={{ color: 'var(--accent-cyan)', margin: '0 8px' }}>•</span>
                  <span>GPU_TEMP</span>
                  <span style={{ color: 'var(--accent-cyan)', margin: '0 8px' }}>•</span>
                  <span>FAN_RPM</span>
                  <span style={{ color: 'var(--accent-cyan)', margin: '0 8px' }}>•</span>
                  <span>CPU_LOAD</span>
                  <span style={{ color: 'var(--accent-cyan)', margin: '0 8px' }}>•</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
