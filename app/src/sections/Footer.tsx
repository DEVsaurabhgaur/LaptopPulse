export default function Footer() {
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
    <footer
      style={{
        backgroundColor: 'var(--bg-surface)',
        paddingTop: 'var(--space-lg)',
        paddingBottom: 'var(--space-md)',
        borderTop: '1px solid var(--border-subtle)',
      }}
    >
      <div className="container-main">
        {/* Top Row */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between">
          {/* Logo */}
          <button
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            className="flex items-center gap-2 cursor-pointer bg-transparent border-none"
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
          <div className="flex items-center flex-wrap" style={{ gap: '32px', marginTop: '16px' }}>
            {navLinks.map((link) => (
              <button
                key={link.id}
                onClick={() => scrollToSection(link.id)}
                className="transition-colors duration-300 cursor-pointer bg-transparent border-none"
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '14px',
                  fontWeight: 500,
                  color: 'var(--text-secondary)',
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

        {/* Divider */}
        <div
          style={{
            height: '1px',
            backgroundColor: 'var(--border-subtle)',
            marginTop: 'var(--space-md)',
          }}
        />

        {/* Bottom Row */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between" style={{ marginTop: 'var(--space-md)' }}>
          <span
            className="font-mono"
            style={{ fontSize: '12px', color: 'var(--text-muted)' }}
          >
            &copy; 2026 Saurabh Gaur. All rights reserved.
          </span>
          <span
            className="font-mono"
            style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '8px' }}
          >
            Built with precision.
          </span>
        </div>
      </div>
    </footer>
  )
}
