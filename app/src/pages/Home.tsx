import Navigation from '../sections/Navigation'
import HeroSection from '../sections/HeroSection'
import ProjectOverview from '../sections/ProjectOverview'
import Architecture from '../sections/Architecture'
import Security from '../sections/Security'
import DevelopmentProcess from '../sections/DevelopmentProcess'
import About from '../sections/About'
import Footer from '../sections/Footer'

export default function Home() {
  return (
    <div style={{ backgroundColor: 'var(--bg-base)', minHeight: '100vh' }}>
      <Navigation />
      <HeroSection />
      <ProjectOverview />
      <Architecture />
      <Security />
      <DevelopmentProcess />
      <About />
      <Footer />
    </div>
  )
}
