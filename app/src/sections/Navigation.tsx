import { useEffect, useRef, useState } from 'react'

export default function Navigation() {
  const [scrolled, setScrolled] = useState(false)
  const navRef = useRef<HTMLElement>(null)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50)
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const scrollToSection = (id: string) => {
    const el = document.getElementById(id)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' })
    }
  }

  const navLinks = [
    { label: 'Architecture', id: 'architecture' },
    { label: 'Security', id: 'security' },
    { label: 'Process', id: 'process' },
    { label: 'About', id: 'about' },
  ]

  return (
    <nav
      ref={navRef}
      className="fixed top-0 left-0 right-0 z-50 transition-all duration-400"
      style={{
        height: '64px',
        backgroundColor: scrolled ? 'rgba(10, 10, 10, 0.8)' : 'rgba(10, 10, 10, 0)',
        backdropFilter: scrolled ? 'blur(12px)' : 'none',
        WebkitBackdropFilter: scrolled ? 'blur(12px)' : 'none',
        borderBottom: scrolled ? '1px solid rgba(255, 255, 255, 0.08)' : '1px solid transparent',
      }}
    >
      <div
        className="flex items-center justify-between h-full"
        style={{
          maxWidth: 'var(--max-width)',
          margin: '0 auto',
          paddingLeft: 'var(--container-pad)',
          paddingRight: 'var(--container-pad)',
        }}
      >
        {/* Logo */}
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          className="flex items-center gap-2 cursor-pointer"
        >
          <img
            src="/logo-icon.png"
            alt="LaptopPulse"
            className="w-5 h-5"
            style={{ filter: 'drop-shadow(0 0 4px rgba(0, 229, 255, 0.5))' }}
          />
          <span
            className="font-mono text-sm tracking-wider"
            style={{ color: 'var(--text-primary)', letterSpacing: '0.05em' }}
          >
            LaptopPulse
          </span>
        </button>

        {/* Nav Links */}
        <div className="hidden md:flex items-center" style={{ gap: '40px' }}>
          {navLinks.map((link) => (
            <button
              key={link.id}
              onClick={() => scrollToSection(link.id)}
              className="font-body text-sm font-medium transition-colors duration-300 cursor-pointer bg-transparent border-none"
              style={{
                color: 'var(--text-secondary)',
                fontFamily: 'var(--font-body)',
                fontSize: '14px',
                fontWeight: 500,
              }}
              onMouseEnter={(e) => {
                (e.target as HTMLElement).style.color = 'var(--accent-cyan)'
              }}
              onMouseLeave={(e) => {
                (e.target as HTMLElement).style.color = 'var(--text-secondary)'
              }}
            >
              {link.label}
            </button>
          ))}
        </div>
      </div>
    </nav>
  )
}
