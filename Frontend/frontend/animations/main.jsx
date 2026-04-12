import React from 'react';
import { createRoot } from 'react-dom/client';
import Hyperspeed from './Hyperspeed';
import Particles from './Particles';
import MagicBento from './MagicBento';
import SplitText from './SplitText';

// ── HOME PAGE: Hyperspeed background ──
const hyperspeedRoot = document.getElementById('hyperspeed-root');
if (hyperspeedRoot) {
  createRoot(hyperspeedRoot).render(
    <React.StrictMode>
      <Hyperspeed />
    </React.StrictMode>
  );
}

// ── DASHBOARD: Particles background ──
const particlesRoot = document.getElementById('particles-root');
if (particlesRoot) {
  createRoot(particlesRoot).render(
    <React.StrictMode>
      <Particles
        particleCount={200}
        particleSpread={10}
        speed={0.1}
        particleColors={['#00ff88', '#00d4ff', '#ffffff']}
        moveParticlesOnHover={true}
        particleHoverFactor={1}
        alphaParticles={true}
        particleBaseSize={100}
        sizeRandomness={1}
        cameraDistance={20}
        disableRotation={false}
      />
    </React.StrictMode>
  );
}

// ── HOME PAGE: SplitText for hero title ──
const splitTitleRoot = document.getElementById('split-title-root');
if (splitTitleRoot) {
  createRoot(splitTitleRoot).render(
    <SplitText
      text="SHELF Scan AI"
      className="hero-title-split"
      delay={80}
      duration={0.8}
      ease="power3.out"
      splitType="chars"
      from={{ opacity: 0, y: 40 }}
      to={{ opacity: 1, y: 0 }}
      threshold={0.1}
      rootMargin="-50px"
      textAlign="center"
      tag="span"
    />
  );
}

// ── HOME PAGE: SplitText for hero subtitle ──
const splitSubRoot = document.getElementById('split-sub-root');
if (splitSubRoot) {
  createRoot(splitSubRoot).render(
    <SplitText
      text="WhatsApp a shelf photo. Our 3-agent AI debate system — Gemini Vision, GPT-4o & Groq — delivers a Hindi voice restock plan in 30 seconds."
      className="hero-sub-split"
      delay={15}
      duration={0.6}
      ease="power3.out"
      splitType="words"
      from={{ opacity: 0, y: 20 }}
      to={{ opacity: 1, y: 0 }}
      threshold={0.1}
      rootMargin="-50px"
      textAlign="center"
      tag="span"
    />
  );
}

// ── HOME PAGE: MagicBento for features ──
const magicBentoRoot = document.getElementById('magic-bento-root');
if (magicBentoRoot) {
  createRoot(magicBentoRoot).render(
    <React.StrictMode>
      <MagicBento
        glowColor="0, 255, 136"
        enableSpotlight={true}
        enableBorderGlow={true}
        enableStars={true}
        enableTilt={true}
        clickEffect={true}
        enableMagnetism={true}
        particleCount={12}
        spotlightRadius={300}
      />
    </React.StrictMode>
  );
}
