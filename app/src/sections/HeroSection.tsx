import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import CyanCircuitry from './CyanCircuitry'

gsap.registerPlugin(ScrollTrigger)

export default function HeroSection() {
  const heroRef = useRef<HTMLDivElement>(null)
  const titleRef = useRef<HTMLHeadingElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)
  const charsRef = useRef<HTMLSpanElement[]>([])

  const titleText = 'LaptopPulse'

  useEffect(() => {
    // 3D Fold-down character animation
    const chars = charsRef.current
    if (chars.length === 0) return

    gsap.set(chars, {
      rotationX: -90,
      transformOrigin: '50% 0%',
      opacity: 0,
      display: 'inline-block',
    })

    const tl = gsap.timeline({ delay: 0.5 })
    tl.to(chars, {
      rotationX: 0,
      opacity: 1,
      duration: 0.6,
      ease: 'power2.out',
      stagger: 0.04,
    })

    // Subtle continuous float after entrance
    chars.forEach((char) => {
      gsap.to(char, {
        y: '+=3',
        duration: 3,
        ease: 'sine.inOut',
        yoyo: true,
        repeat: -1,
        delay: Math.random() * 2,
      })
    })

    // Scroll shrink effect
    if (titleRef.current) {
      gsap.to(titleRef.current, {
        scale: 0.6,
        opacity: 0,
        scrollTrigger: {
          trigger: heroRef.current,
          start: 'top top',
          end: '50% top',
          scrub: true,
        },
      })
    }

    // Content fade on scroll
    if (contentRef.current) {
      gsap.to(contentRef.current, {
        opacity: 0,
        y: -30,
        scrollTrigger: {
          trigger: heroRef.current,
          start: 'top top',
          end: '40% top',
          scrub: true,
        },
      })
    }

    return () => {
      tl.kill()
      ScrollTrigger.getAll().forEach((st) => st.kill())
    }
  }, [])

  const setCharRef = (index: number) => (el: HTMLSpanElement | null) => {
    if (el) charsRef.current[index] = el
  }

  return (
    <section
      ref={heroRef}
      id="hero"
      className="relative overflow-hidden"
      style={{ height: '100vh', backgroundColor: 'var(--bg-base)' }}
    >
      {/* 3D Canvas Background */}
      <CyanCircuitry className="absolute inset-0 z-0" />

      {/* Bottom gradient overlay */}
      <div
        className="absolute inset-0 z-[1] pointer-events-none"
        style={{
          background: 'linear-gradient(to top, rgba(0,0,0,0.7) 0%, transparent 50%)',
        }}
      />

      {/* Hero Content */}
      <div
        ref={contentRef}
        className="relative z-10 flex flex-col justify-end h-full pointer-events-none"
        style={{
          paddingLeft: 'var(--container-pad)',
          paddingRight: 'var(--container-pad)',
          paddingBottom: 'var(--space-hero)',
          maxWidth: 'var(--max-width)',
        }}
      >
        {/* Eyebrow */}
        <span
          className="font-mono uppercase"
          style={{
            fontSize: '12px',
            color: 'var(--text-muted)',
            letterSpacing: '0.15em',
            marginBottom: 'var(--space-sm)',
          }}
        >
          Software Engineering Portfolio
        </span>

        {/* Title with 3D fold animation */}
        <h1
          ref={titleRef}
          className="font-heading"
          style={{
            fontSize: 'clamp(48px, 8vw, 96px)',
            fontWeight: 400,
            lineHeight: 1.0,
            color: 'var(--text-primary)',
            perspective: '1000px',
          }}
        >
          {titleText.split('').map((char, i) => (
            <span
              key={i}
              ref={setCharRef(i)}
              style={{
                display: 'inline-block',
                transformStyle: 'preserve-3d',
              }}
            >
              {char}
            </span>
          ))}
        </h1>

        {/* Subtitle */}
        <p
          className="font-heading"
          style={{
            fontSize: 'clamp(20px, 3vw, 32px)',
            fontWeight: 300,
            color: 'var(--text-secondary)',
            maxWidth: '560px',
            lineHeight: 1.5,
            marginTop: 'var(--space-md)',
          }}
        >
          An AI-powered hardware health monitor. Silent watcher. Anomaly detector. Built with systems thinking.
        </p>

        {/* CTA Row */}
        <div
          className="flex items-center pointer-events-auto"
          style={{ gap: 'var(--space-sm)', marginTop: 'var(--space-lg)' }}
        >
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block transition-all duration-300"
            style={{
              fontFamily: 'var(--font-body)',
              fontSize: '16px',
              fontWeight: 600,
              color: 'var(--accent-cyan)',
              border: '1px solid var(--accent-cyan)',
              padding: '12px 28px',
              borderRadius: '4px',
              textDecoration: 'none',
            }}
            onMouseEnter={(e) => {
              (e.target as HTMLElement).style.backgroundColor = 'var(--accent-cyan-dim)'
            }}
            onMouseLeave={(e) => {
              (e.target as HTMLElement).style.backgroundColor = 'transparent'
            }}
          >
            View on GitHub
          </a>
          <button
            onClick={() => document.getElementById('about')?.scrollIntoView({ behavior: 'smooth' })}
            className="inline-block transition-all duration-300 cursor-pointer bg-transparent"
            style={{
              fontFamily: 'var(--font-body)',
              fontSize: '16px',
              fontWeight: 600,
              color: 'var(--text-secondary)',
              border: '1px solid var(--border-subtle)',
              padding: '12px 28px',
              borderRadius: '4px',
            }}
            onMouseEnter={(e) => {
              const el = e.target as HTMLElement
              el.style.borderColor = 'var(--border-active)'
              el.style.color = 'var(--text-primary)'
            }}
            onMouseLeave={(e) => {
              const el = e.target as HTMLElement
              el.style.borderColor = 'var(--border-subtle)'
              el.style.color = 'var(--text-secondary)'
            }}
          >
            Read the Blueprint
          </button>
        </div>
      </div>
    </section>
  )
}
