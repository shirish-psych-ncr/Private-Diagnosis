// ============================================
// FLUSH Particle Effect - DOM-to-Pixel Vortex
// Combines techniques from TEXTure.js, P5.js, Pts.js, D3-Force, and Matter.js
// ============================================

class FlushParticleEffect {
    constructor() {
        this.canvas = document.getElementById('particle-canvas');
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
        this.button = document.getElementById('flush-btn');
        this.particles = [];
        this.domElements = [];
        this.animationId = null;
        this.isActive = false;
        this.vortexCenter = { x: 0, y: 0 };
        this.vortexStrength = 0.15;
        this.decayRate = 0.98;
        this.angularSpeed = 0.08;
        
        if (this.canvas && this.button) {
            this.init();
        }
    }

    init() {
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
        this.button.addEventListener('click', () => this.triggerFlush());
    }

    resizeCanvas() {
        if (!this.canvas) return;
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.vortexCenter = {
            x: this.canvas.width / 2,
            y: this.canvas.height / 2
        };
    }

    captureDOMElements() {
        // Capture all visible DOM elements for particle conversion
        const selectors = [
            '.service-card', '.therapist-card', '.hero-title', 
            '.hero-subtitle', '.stat', '.feature', 'nav', 'footer'
        ];
        
        this.domElements = [];
        selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    this.domElements.push({
                        element: el,
                        x: rect.left + rect.width / 2,
                        y: rect.top + rect.height / 2,
                        width: rect.width,
                        height: rect.height,
                        opacity: parseFloat(getComputedStyle(el).opacity) || 1
                    });
                }
            });
        });
    }

    createParticlesFromDOM() {
        this.particles = [];
        
        // Create particles from DOM element bounds (TEXTure.js style)
        this.domElements.forEach(dom => {
            const particleCount = Math.floor((dom.width * dom.height) / 200);
            
            for (let i = 0; i < Math.min(particleCount, 50); i++) {
                // Random position within DOM element bounds
                const offsetX = (Math.random() - 0.5) * dom.width * 0.8;
                const offsetY = (Math.random() - 0.5) * dom.height * 0.8;
                
                // Get color from element or use default
                const color = this.getElementColor(dom.element);
                
                this.particles.push({
                    x: dom.x + offsetX,
                    y: dom.y + offsetY,
                    originX: dom.x + offsetX,
                    originY: dom.y + offsetY,
                    vx: 0,
                    vy: 0,
                    radius: Math.random() * 3 + 1,
                    color: color,
                    angle: Math.atan2(dom.y - this.vortexCenter.y, dom.x - this.vortexCenter.x),
                    baseRadius: Math.sqrt(
                        Math.pow(dom.x - this.vortexCenter.x, 2) + 
                        Math.pow(dom.y - this.vortexCenter.y, 2)
                    ),
                    decay: 0.96 + Math.random() * 0.03,
                    angularVelocity: (Math.random() - 0.5) * 0.1 + this.angularSpeed,
                    life: 1,
                    lifeDecay: 0.005 + Math.random() * 0.01
                });
            }
        });
    }

    getElementColor(element) {
        const colors = ['#4a90a4', '#7eb8a3', '#6ab0c3', '#667eea', '#764ba2'];
        const computedColor = getComputedStyle(element).color;
        
        if (computedColor && computedColor !== 'rgb(0, 0, 0)') {
            return computedColor;
        }
        
        return colors[Math.floor(Math.random() * colors.length)];
    }

    triggerFlush() {
        if (this.isActive) return;
        
        this.isActive = true;
        this.canvas.classList.add('active');
        
        // Hide page content temporarily
        document.body.style.overflow = 'hidden';
        
        // Capture DOM and create particles
        this.captureDOMElements();
        this.createParticlesFromDOM();
        
        // Start animation loop
        this.animate();
        
        // Auto-reset after 5 seconds
        setTimeout(() => this.reset(), 5000);
    }

    animate() {
        if (!this.isActive) return;
        
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Update and draw particles
        this.particles.forEach(particle => {
            // Calculate distance to vortex center
            const dx = this.vortexCenter.x - particle.x;
            const dy = this.vortexCenter.y - particle.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            // Calculate current angle
            const currentAngle = Math.atan2(dy, dx);
            
            // VORTEX FORCE: Tangential spin + radial pull (Matter.js/D3-Force style)
            // Tangential force (spin)
            const tangentX = -Math.sin(currentAngle);
            const tangentY = Math.cos(currentAngle);
            
            // Radial force (pull to center)
            const radialForce = this.vortexStrength * (100 / (distance + 1));
            const radialX = Math.cos(currentAngle) * radialForce;
            const radialY = Math.sin(currentAngle) * radialForce;
            
            // Apply forces to velocity
            particle.vx += tangentX * this.angularSpeed * 5 + radialX;
            particle.vy += tangentY * this.angularSpeed * 5 + radialY;
            
            // Apply decay (viscous inertia)
            particle.vx *= this.decayRate;
            particle.vy *= this.decayRate;
            
            // Update position
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            // Decay radius (P5.js style)
            particle.radius *= particle.decay;
            
            // Update life
            particle.life -= particle.lifeDecay;
            
            // Draw particle
            this.drawParticle(particle);
        });
        
        // Remove dead particles
        this.particles = this.particles.filter(p => p.life > 0 && p.radius > 0.1);
        
        // Continue animation if particles remain
        if (this.particles.length > 0) {
            this.animationId = requestAnimationFrame(() => this.animate());
        } else {
            this.reset();
        }
    }

    drawParticle(particle) {
        if (!this.ctx) return;
        
        this.ctx.beginPath();
        this.ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
        
        // Parse color and add alpha based on life
        let rgba = particle.color;
        if (particle.color.startsWith('rgb')) {
            rgba = particle.color.replace('rgb', 'rgba').replace(')', `, ${particle.life})`);
        } else {
            this.ctx.globalAlpha = particle.life;
        }
        
        this.ctx.fillStyle = rgba;
        this.ctx.fill();
        this.ctx.globalAlpha = 1;
    }

    reset() {
        this.isActive = false;
        this.canvas.classList.remove('active');
        document.body.style.overflow = '';
        
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.particles = [];
    }
}

// Initialize FLUSH effect when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const flushEffect = new FlushParticleEffect();
    window.flushEffect = flushEffect;
});
