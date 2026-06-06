import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const layers = [
  {
    num: '01',
    name: 'Silent Watcher Daemon',
    desc: 'Collects raw sensor data every 60 sec — CPU temp, GPU temp, fan RPM, battery health. Uses < 0.3% CPU.',
    status: 'ALWAYS ON',
    statusColor: 'var(--accent-green)',
  },
  {
    num: '02',
    name: 'Anomaly Detector',
    desc: 'Rule-based + trend analysis engine. Threshold rules for immediate danger + 30/60/90-day trend detection.',
    status: 'ALWAYS ON',
    statusColor: 'var(--accent-green)',
  },
  {
    num: '03',
    name: 'Log Accumulator',
    desc: 'Stores compressed daily JSONL logs. 90-day auto-rotation. ~120KB/month total storage. Zero cloud.',
    status: 'ALWAYS ON',
    statusColor: 'var(--accent-green)',
  },
  {
    num: '04',
    name: 'AI Report Generator',
    desc: 'Fires once on anomaly detection. Aggregates 30 days of logs, calls Claude API, generates HTML report. Then sleeps.',
    status: 'EVENT ONLY',
    statusColor: 'var(--accent-amber)',
  },
]

export default function Architecture() {
  const sectionRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.utils.toArray<HTMLElement>('.arch-header').forEach((el) => {
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

      gsap.utils.toArray<HTMLElement>('.arch-band').forEach((el, i) => {
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
          delay: i * 0.15,
        })
      })

      gsap.from('.arch-footer', {
        opacity: 0,
        y: 20,
        duration: 0.8,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: '.arch-footer',
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
      id="architecture"
      style={{
        backgroundColor: 'var(--bg-surface)',
        paddingTop: 'var(--space-xl)',
        paddingBottom: 'var(--space-xl)',
      }}
    >
      <div className="container-main">
        {/* Section Header */}
        <div className="arch-header text-center" style={{ marginBottom: 'var(--space-lg)' }}>
          <span
            className="font-mono uppercase block"
            style={{
              fontSize: '12px',
              color: 'var(--text-muted)',
              letterSpacing: '0.15em',
            }}
          >
            System Architecture
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
            Four-Layer Design
          </h2>
        </div>

        {/* Architecture Stack */}
        <div className="flex flex-col" style={{ gap: '16px' }}>
          {layers.map((layer) => (
            <div
              key={layer.num}
              className="arch-band flex flex-col md:flex-row items-start md:items-center transition-all duration-400"
              style={{
                border: '1px solid var(--border-subtle)',
                borderRadius: '8px',
                padding: 'var(--space-md)',
                minHeight: '120px',
                cursor: 'default',
              }}
              onMouseEnter={(e) => {
                const el = e.currentTarget
                el.style.borderColor = 'var(--border-active)'
                el.style.boxShadow = '0 0 20px var(--accent-cyan-dim)'
              }}
              onMouseLeave={(e) => {
                const el = e.currentTarget
                el.style.borderColor = 'var(--border-subtle)'
                el.style.boxShadow = 'none'
              }}
            >
              {/* Layer Number */}
              <span
                className="font-mono shrink-0"
                style={{
                  fontSize: '32px',
                  color: 'var(--text-muted)',
                  minWidth: '60px',
                }}
              >
                {layer.num}
              </span>

              {/* Layer Name */}
              <span
                className="shrink-0"
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '18px',
                  color: 'var(--text-primary)',
                  fontWeight: 400,
                  minWidth: '240px',
                  marginLeft: '16px',
                }}
              >
                {layer.name}
              </span>

              {/* Description */}
              <span
                className="flex-1"
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '16px',
                  color: 'var(--text-secondary)',
                  marginLeft: '24px',
                  marginTop: '8px',
                  lineHeight: 1.5,
                }}
              >
                {layer.desc}
              </span>

              {/* Status Pill */}
              <span
                className="font-mono shrink-0 mt-2 md:mt-0"
                style={{
                  fontSize: '11px',
                  padding: '4px 12px',
                  borderRadius: '4px',
                  backgroundColor: layer.statusColor,
                  color: '#000000',
                  fontWeight: 600,
                  marginLeft: '16px',
                }}
              >
                {layer.status}
              </span>
            </div>
          ))}
        </div>

        {/* Footer Quote */}
        <p
          className="arch-footer text-center"
          style={{
            fontFamily: 'var(--font-body)',
            fontSize: '16px',
            color: 'var(--text-secondary)',
            maxWidth: '640px',
            margin: '0 auto',
            marginTop: 'var(--space-md)',
            fontStyle: 'italic',
            lineHeight: 1.6,
          }}
        >
          Each layer is independently replaceable. The event-driven design means the AI engine — the 
          heaviest component — only fires when needed, then sleeps.
        </p>
      </div>
    </section>
  )
}
