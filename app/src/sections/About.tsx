import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export default function About() {
  const sectionRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.utils.toArray<HTMLElement>('.about-animate').forEach((el, i) => {
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
      id="about"
      style={{
        backgroundColor: 'var(--bg-base)',
        paddingTop: 'var(--space-xl)',
        paddingBottom: 'var(--space-xl)',
      }}
    >
      <div className="container-main">
        <div
          className="grid grid-cols-1 md:grid-cols-2 items-center"
          style={{ gap: 'var(--space-lg)' }}
        >
          {/* Left Column */}
          <div>
            <span
              className="about-animate font-mono uppercase block"
              style={{
                fontSize: '12px',
                color: 'var(--text-muted)',
                letterSpacing: '0.15em',
              }}
            >
              About
            </span>
            <h2
              className="about-animate font-heading"
              style={{
                fontSize: 'clamp(32px, 5vw, 64px)',
                fontWeight: 400,
                color: 'var(--text-primary)',
                marginTop: '8px',
              }}
            >
              Engineer. Author. Builder.
            </h2>
            <p
              className="about-animate"
              style={{
                fontFamily: 'var(--font-body)',
                fontSize: '18px',
                color: 'var(--text-secondary)',
                lineHeight: 1.7,
                marginTop: 'var(--space-md)',
              }}
            >
              I'm Saurabh Gaur — a software engineer who believes systems thinking is the difference 
              between code that works once and software that works for years. LaptopPulse is the 
              product of that philosophy: a complete hardware health monitoring system built from 
              first principles, covering every phase from requirement analysis to deployment packaging. 
              The accompanying Software Engineering Master Guide documents the methodology — memory 
              management, encryption, language selection, and professional documentation — so the 
              knowledge outlives the codebase.
            </p>
            <a
              href="#"
              className="about-animate inline-block transition-opacity duration-300"
              style={{
                fontFamily: 'var(--font-body)',
                fontSize: '16px',
                fontWeight: 600,
                color: 'var(--accent-cyan)',
                textDecoration: 'underline',
                textUnderlineOffset: '4px',
                marginTop: 'var(--space-md)',
              }}
              onMouseEnter={(e) => {
                (e.target as HTMLElement).style.opacity = '0.7'
              }}
              onMouseLeave={(e) => {
                (e.target as HTMLElement).style.opacity = '1'
              }}
            >
              Read the Full Guide
            </a>
          </div>

          {/* Right Column - Profile Card */}
          <div className="about-animate flex justify-center">
            <div
              style={{
                backgroundColor: 'var(--bg-surface)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '12px',
                padding: 'var(--space-lg)',
                textAlign: 'center',
                maxWidth: '320px',
                width: '100%',
              }}
            >
              {/* Profile Image */}
              <div
                className="mx-auto overflow-hidden"
                style={{
                  width: '200px',
                  height: '200px',
                  borderRadius: '50%',
                  border: '2px solid var(--border-subtle)',
                }}
              >
                <img
                  src="/profile-pattern.jpg"
                  alt="Saurabh Gaur"
                  className="w-full h-full object-cover"
                />
              </div>

              <h3
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '18px',
                  color: 'var(--text-primary)',
                  marginTop: 'var(--space-md)',
                  fontWeight: 500,
                }}
              >
                Saurabh Gaur
              </h3>
              <p
                className="font-mono"
                style={{
                  fontSize: '12px',
                  color: 'var(--text-muted)',
                  marginTop: '4px',
                }}
              >
                Software Engineer
              </p>

              {/* Social Links */}
              <div
                className="flex items-center justify-center"
                style={{ gap: 'var(--space-sm)', marginTop: 'var(--space-sm)' }}
              >
                {/* GitHub */}
                <a
                  href="https://github.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="transition-colors duration-300"
                  style={{ color: 'var(--text-muted)' }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLElement).style.color = 'var(--accent-cyan)'
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLElement).style.color = 'var(--text-muted)'
                  }}
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                  </svg>
                </a>
                {/* LinkedIn */}
                <a
                  href="https://linkedin.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="transition-colors duration-300"
                  style={{ color: 'var(--text-muted)' }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLElement).style.color = 'var(--accent-cyan)'
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLElement).style.color = 'var(--text-muted)'
                  }}
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                  </svg>
                </a>
                {/* Twitter */}
                <a
                  href="https://twitter.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="transition-colors duration-300"
                  style={{ color: 'var(--text-muted)' }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLElement).style.color = 'var(--accent-cyan)'
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLElement).style.color = 'var(--text-muted)'
                  }}
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
