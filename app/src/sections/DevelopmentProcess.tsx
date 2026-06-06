import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const weeks = [
  { num: '01', title: 'Foundation', desc: 'Install Python 3.11, psutil, LibreHardwareMonitor. Write watcher.py — reads CPU/GPU temp + fan RPM. Test on TUF A15. 24 hours of clean log data.' },
  { num: '02', title: 'Anomaly Detection', desc: 'Build threshold.py with all 10 core rules. Build trend.py — 7-day baseline + 30-day delta. Unit test every rule with mock data.' },
  { num: '03', title: 'Storage', desc: 'Build logger.py — compressed daily JSONL. Build baseline.py — capture first 7-day profile. Build trends_calc.py — rolling averages.' },
  { num: '04', title: 'Service Shell', desc: 'Install pywin32 — register as Windows Service. Build tray.py — green/yellow/red icon states. Right-click menu: View Status, View Reports, Settings.' },
  { num: '05', title: 'AI Engine', desc: 'Integrate Claude API (claude-sonnet-4-20250514). Write prompt templates for each anomaly type. Build html_render.py — dark-themed report output.' },
  { num: '06', title: 'Edge Cases', desc: 'Handle edge cases: no NVIDIA GPU, WMI failures. Add AMD GPU support (rocm-smi / WMI fallback). Add offline mode (rule-based report without AI).' },
  { num: '07', title: 'Packaging', desc: 'PyInstaller: package into single .exe. Inno Setup: create proper Windows installer. Test install/uninstall on clean Windows 11 VM.' },
  { num: '08', title: 'Beta Launch', desc: 'Post on r/hardware, r/india, r/laptops. Post on Twitter/X with demo video. First 100 users: FREE (collect feedback).' },
]

export default function DevelopmentProcess() {
  const sectionRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.utils.toArray<HTMLElement>('.process-header').forEach((el) => {
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
        })
      })

      gsap.utils.toArray<HTMLElement>('.process-card').forEach((el, i) => {
        gsap.from(el, {
          opacity: 0,
          y: 30,
          duration: 0.8,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: el,
            start: 'top 85%',
            toggleActions: 'play none none none',
          },
          delay: (i % 4) * 0.08,
        })
      })

      gsap.from('.process-footer', {
        opacity: 0,
        y: 20,
        duration: 0.8,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: '.process-footer',
          start: 'top 85%',
          toggleActions: 'play none none none',
        },
      })
    }, sectionRef)

    return () => ctx.revert()
  }, [])

  return (
    <section
      ref={sectionRef}
      id="process"
      style={{
        backgroundColor: 'var(--bg-surface)',
        paddingTop: 'var(--space-xl)',
        paddingBottom: 'var(--space-xl)',
      }}
    >
      <div className="container-main">
        {/* Section Header */}
        <div className="process-header text-center" style={{ marginBottom: 'var(--space-lg)' }}>
          <span
            className="font-mono uppercase block"
            style={{
              fontSize: '12px',
              color: 'var(--text-muted)',
              letterSpacing: '0.15em',
            }}
          >
            The Build
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
            8-Week Execution
          </h2>
        </div>

        {/* Timeline Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4" style={{ gap: 'var(--space-sm)' }}>
          {weeks.map((week) => (
            <div
              key={week.num}
              className="process-card transition-all duration-300"
              style={{
                backgroundColor: 'var(--bg-base)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '8px',
                padding: 'var(--space-md)',
                minHeight: '180px',
                cursor: 'default',
              }}
              onMouseEnter={(e) => {
                const el = e.currentTarget
                el.style.borderColor = 'var(--border-active)'
                el.style.transform = 'translateY(-4px)'
              }}
              onMouseLeave={(e) => {
                const el = e.currentTarget
                el.style.borderColor = 'var(--border-subtle)'
                el.style.transform = 'translateY(0)'
              }}
            >
              <span
                className="font-mono block"
                style={{
                  fontSize: '11px',
                  color: 'var(--accent-cyan)',
                  letterSpacing: '0.1em',
                }}
              >
                WEEK {week.num}
              </span>
              <h3
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '16px',
                  fontWeight: 600,
                  color: 'var(--text-primary)',
                  marginTop: '8px',
                }}
              >
                {week.title}
              </h3>
              <p
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '14px',
                  color: 'var(--text-secondary)',
                  marginTop: '8px',
                  lineHeight: 1.6,
                }}
              >
                {week.desc}
              </p>
            </div>
          ))}
        </div>

        {/* Footer Quote */}
        <p
          className="process-footer text-center"
          style={{
            fontFamily: 'var(--font-body)',
            fontSize: '16px',
            color: 'var(--text-secondary)',
            maxWidth: '560px',
            margin: '0 auto',
            marginTop: 'var(--space-md)',
            fontStyle: 'italic',
            lineHeight: 1.6,
          }}
        >
          Every phase was executed in sequence: Requirements → System Design → Technology Selection 
          → Implementation → Testing → Security Hardening → Deployment → Maintenance. No shortcuts.
        </p>
      </div>
    </section>
  )
}
