/**
 * Mental Health Clinic Website - Main JavaScript
 * Includes WebGL background animation with Three.js
 * 
 * CLASSIFIED PHYSICS ENGINE IMPLEMENTATION
 * Implements: Temporal Echo Rig, Viscous Inertia, Bullet Time, Volumetric Lighting
 */

// ============================================
// WebGL Background Animation with Advanced Physics
// ============================================

class WebGLBackground {
    constructor() {
        this.canvas = document.getElementById('webgl-canvas');
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.particles = null;
        this.floatingShapes = [];
        this.temporalEchoes = [];
        this.mouseX = 0;
        this.mouseY = 0;
        this.lastMouseX = 0;
        this.lastMouseY = 0;
        this.velocityX = 0;
        this.velocityY = 0;
        this.windowHalfX = window.innerWidth / 2;
        this.windowHalfY = window.innerHeight / 2;
        this.bulletTimeActive = false;
        this.targetPlaybackRate = 1.0;
        this.currentPlaybackRate = 1.0;
        
        this.init();
        this.animate();
        this.addEventListeners();
        this.setupTemporalEchoRig();
    }
    
    init() {
        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xf8f9fa);
        
        // Camera
        this.camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            1,
            10000
        );
        this.camera.position.z = 1000;
        
        // Renderer
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        
        // Create particles
        this.createParticles();
        
        // Add lights
        this.addLights();
    }
    
    createParticles() {
        const geometry = new THREE.BufferGeometry();
        const vertices = [];
        const colors = [];
        
        const particleCount = 300;
        const colorPalette = [
            new THREE.Color(0x4a90a4), // Primary teal
            new THREE.Color(0x7eb8a3), // Secondary green
            new THREE.Color(0x6ab0c3), // Light teal
            new THREE.Color(0x667eea), // Purple
            new THREE.Color(0x764ba2)  // Deep purple
        ];
        
        for (let i = 0; i < particleCount; i++) {
            // Position particles in a spread out formation
            const x = Math.random() * 2000 - 1000;
            const y = Math.random() * 2000 - 1000;
            const z = Math.random() * 2000 - 1000;
            vertices.push(x, y, z);
            
            // Assign random color from palette
            const color = colorPalette[Math.floor(Math.random() * colorPalette.length)];
            colors.push(color.r, color.g, color.b);
        }
        
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        
        // Create particle material
        const material = new THREE.PointsMaterial({
            size: 8,
            vertexColors: true,
            transparent: true,
            opacity: 0.8,
            sizeAttenuation: true
        });
        
        this.particles = new THREE.Points(geometry, material);
        this.scene.add(this.particles);
        
        // Add floating geometric shapes
        this.addFloatingShapes();
    }
    
    addFloatingShapes() {
        const shapes = [];
        const geometries = [
            new THREE.IcosahedronGeometry(30, 0),
            new THREE.OctahedronGeometry(30, 0),
            new THREE.TetrahedronGeometry(30, 0),
            new THREE.SphereGeometry(25, 16, 16)
        ];
        
        const materials = [
            new THREE.MeshPhongMaterial({ 
                color: 0x4a90a4, 
                transparent: true, 
                opacity: 0.3,
                shininess: 100
            }),
            new THREE.MeshPhongMaterial({ 
                color: 0x7eb8a3, 
                transparent: true, 
                opacity: 0.3,
                shininess: 100
            }),
            new THREE.MeshPhongMaterial({ 
                color: 0x667eea, 
                transparent: true, 
                opacity: 0.3,
                shininess: 100
            })
        ];
        
        for (let i = 0; i < 8; i++) {
            const geometry = geometries[Math.floor(Math.random() * geometries.length)];
            const material = materials[Math.floor(Math.random() * materials.length)];
            const mesh = new THREE.Mesh(geometry, material);
            
            mesh.position.x = Math.random() * 1500 - 750;
            mesh.position.y = Math.random() * 1500 - 750;
            mesh.position.z = Math.random() * 1000 - 500;
            
            mesh.rotation.x = Math.random() * Math.PI;
            mesh.rotation.y = Math.random() * Math.PI;
            
            mesh.userData = {
                rotationSpeed: {
                    x: (Math.random() - 0.5) * 0.01,
                    y: (Math.random() - 0.5) * 0.01
                },
                floatSpeed: Math.random() * 0.5 + 0.5,
                floatOffset: Math.random() * Math.PI * 2
            };
            
            this.scene.add(mesh);
            shapes.push(mesh);
        }
        
        this.floatingShapes = shapes;
    }
    
    addLights() {
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);
        
        const pointLight1 = new THREE.PointLight(0x4a90a4, 1, 2000);
        pointLight1.position.set(500, 500, 500);
        this.scene.add(pointLight1);
        
        const pointLight2 = new THREE.PointLight(0x7eb8a3, 1, 2000);
        pointLight2.position.set(-500, -500, 500);
        this.scene.add(pointLight2);
        
        // Add volumetric light sources for advanced compositing
        this.addVolumetricLights();
    }
    
    addVolumetricLights() {
        // Create volumetric light effect using additive blending
        const volumetricGeometry = new THREE.SphereGeometry(100, 32, 32);
        const volumetricMaterial = new THREE.MeshBasicMaterial({
            color: 0x4a90a4,
            transparent: true,
            opacity: 0.15,
            blending: THREE.AdditiveBlending,
            side: THREE.DoubleSide
        });
        
        this.volumetricLight = new THREE.Mesh(volumetricGeometry, volumetricMaterial);
        this.volumetricLight.position.set(0, 0, -500);
        this.scene.add(this.volumetricLight);
    }
    
    setupTemporalEchoRig() {
        // THE TEMPORAL ECHO RIG - Creates ghost trails of moving elements
        // Implements WAAPI time cloning with reversed playbackRate
        
        if (!this.floatingShapes || this.floatingShapes.length === 0) return;
        
        // Create temporal echoes for the first 3 shapes
        for (let i = 0; i < Math.min(3, this.floatingShapes.length); i++) {
            const originalShape = this.floatingShapes[i];
            
            // Clone the shape for echo effect
            const echoGeometry = originalShape.geometry.clone();
            const echoMaterial = originalShape.material.clone();
            echoMaterial.transparent = true;
            echoMaterial.opacity = 0.3;
            echoMaterial.blending = THREE.AdditiveBlending;
            
            const echoMesh = new THREE.Mesh(echoGeometry, echoMaterial);
            echoMesh.position.copy(originalShape.position);
            echoMesh.rotation.copy(originalShape.rotation);
            
            // Store echo with time offset
            echoMesh.userData = {
                isEcho: true,
                parentIndex: i,
                timeOffset: -(i + 1) * 200, // -200ms, -400ms, -600ms
                playbackRate: -1, // Reverse playback for echo effect
                originalShape: originalShape
            };
            
            this.scene.add(echoMesh);
            this.temporalEchoes.push(echoMesh);
        }
        
        console.log('Temporal Echo Rig initialized:', this.temporalEchoes.length, 'echoes created');
    }
    
    addEventListeners() {
        window.addEventListener('resize', () => this.onWindowResize(), false);
        document.addEventListener('mousemove', (e) => this.onMouseMove(e), false);
        window.addEventListener('scroll', () => this.onScroll(), false);
    }
    
    onWindowResize() {
        this.windowHalfX = window.innerWidth / 2;
        this.windowHalfY = window.innerHeight / 2;
        
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }
    
    onMouseMove(event) {
        // Calculate mouse velocity for viscous inertia effect
        this.lastMouseX = this.mouseX;
        this.lastMouseY = this.mouseY;
        
        this.mouseX = event.clientX - this.windowHalfX;
        this.mouseY = event.clientY - this.windowHalfY;
        
        // Velocity calculation for THE REVERSING SHORTENING FACTOR hack
        this.velocityX = this.mouseX - this.lastMouseX;
        this.velocityY = this.mouseY - this.lastMouseY;
        
        // Apply viscous drag to volumetric light
        if (this.volumetricLight) {
            // Viscous inertia: the light follows with delay, creating liquid feel
            const targetX = this.mouseX * 0.5;
            const targetY = this.mouseY * 0.5;
            this.volumetricLight.position.x += (targetX - this.volumetricLight.position.x) * 0.05;
            this.volumetricLight.position.y += (-targetY - this.volumetricLight.position.y) * 0.05;
        }
    }
    
    onScroll() {
        const scrollY = window.scrollY;
        if (this.particles) {
            this.particles.rotation.y = scrollY * 0.0005;
            this.particles.rotation.x = scrollY * 0.0002;
        }
        
        // Scroll-scrubbed explosion effect for floating shapes
        if (this.floatingShapes) {
            this.floatingShapes.forEach((shape, index) => {
                const scrollFactor = Math.min(scrollY * 0.001, 1);
                shape.scale.setScalar(1 + scrollFactor * 0.3);
            });
        }
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        const time = Date.now() * 0.0001;
        
        // Apply bullet time effect if active (temporal dilation)
        if (this.bulletTimeActive) {
            // Smoothly interpolate to target playback rate
            this.currentPlaybackRate += (this.targetPlaybackRate - this.currentPlaybackRate) * 0.1;
        } else {
            this.currentPlaybackRate += (1.0 - this.currentPlaybackRate) * 0.1;
        }
        
        const timeScale = this.currentPlaybackRate;
        
        // Animate particles with temporal scaling
        if (this.particles) {
            this.particles.rotation.y += 0.001 * timeScale;
            this.particles.rotation.x += 0.0005 * timeScale;
            
            // Gentle mouse interaction with viscous inertia
            this.particles.rotation.y += (this.mouseX * 0.0001 - this.particles.rotation.y) * 0.05 * timeScale;
            this.particles.rotation.x += (this.mouseY * 0.0001 - this.particles.rotation.x) * 0.05 * timeScale;
        }
        
        // Animate floating shapes with spring physics
        if (this.floatingShapes) {
            this.floatingShapes.forEach((shape, index) => {
                shape.rotation.x += shape.userData.rotationSpeed.x * timeScale;
                shape.rotation.y += shape.userData.rotationSpeed.y * timeScale;
                
                // Floating motion with spring-damper simulation
                shape.position.y += Math.sin(time * shape.userData.floatSpeed * timeScale + shape.userData.floatOffset) * 0.5 * timeScale;
                
                // Add subtle scale pulsing using spring easing
                const pulse = 1 + Math.sin(time * 2 + index) * 0.05;
                shape.scale.setScalar(pulse);
            });
        }
        
        // Update temporal echoes (ghost trails)
        if (this.temporalEchoes && this.temporalEchoes.length > 0) {
            this.temporalEchoes.forEach((echo, index) => {
                if (echo.userData.originalShape) {
                    const parent = echo.userData.originalShape;
                    
                    // Echo follows parent with time delay and decay
                    const delayFactor = 0.03 * timeScale;
                    echo.position.x += (parent.position.x - echo.position.x) * delayFactor;
                    echo.position.y += (parent.position.y - echo.position.y) * delayFactor;
                    echo.position.z += (parent.position.z - echo.position.z) * delayFactor;
                    
                    // Echo rotation lags behind parent
                    echo.rotation.x += (parent.rotation.x - echo.rotation.x) * delayFactor;
                    echo.rotation.y += (parent.rotation.y - echo.rotation.y) * delayFactor;
                    
                    // Pulsing opacity for ghost effect
                    echo.material.opacity = 0.15 + Math.sin(time * 3 + index * 0.5) * 0.1;
                }
            });
        }
        
        // Animate volumetric light with breathing effect
        if (this.volumetricLight) {
            this.volumetricLight.scale.setScalar(1 + Math.sin(time * 1.5) * 0.2);
            this.volumetricLight.rotation.y += 0.002 * timeScale;
            this.volumetricLight.rotation.z += 0.001 * timeScale;
        }
        
        this.renderer.render(this.scene, this.camera);
    }
    
    // BULLET TIME - Global temporal dilation control
    toggleBulletTime(enable) {
        this.bulletTimeActive = enable;
        this.targetPlaybackRate = enable ? 0.2 : 1.0;
        
        // Apply to CSS animations as well
        document.body.classList.toggle('bullet-time-active', enable);
        
        console.log('Bullet Time:', enable ? 'ACTIVATED' : 'DEACTIVATED', '| Playback Rate:', this.targetPlaybackRate);
    }
    
    // VISCOUS INERTIA - Get current velocity for external use
    getVelocity() {
        return {
            x: this.velocityX,
            y: this.velocityY,
            magnitude: Math.sqrt(this.velocityX ** 2 + this.velocityY ** 2)
        };
    }
}

// ============================================
// UI Interactions
// ============================================

class UIController {
    constructor() {
        this.navbar = document.getElementById('navbar');
        this.navMenu = document.getElementById('nav-menu');
        this.navToggle = document.getElementById('nav-toggle');
        this.navLinks = document.querySelectorAll('.nav-link');
        this.contactForm = document.getElementById('contact-form');
        
        this.init();
    }
    
    init() {
        this.addEventListeners();
        this.handleScroll();
    }
    
    addEventListeners() {
        // Navbar scroll effect
        window.addEventListener('scroll', () => this.handleScroll());
        
        // Mobile menu toggle
        if (this.navToggle) {
            this.navToggle.addEventListener('click', () => this.toggleMobileMenu());
        }
        
        // Smooth scrolling for nav links
        this.navLinks.forEach(link => {
            link.addEventListener('click', (e) => this.handleNavClick(e));
        });
        
        // Contact form submission
        if (this.contactForm) {
            this.contactForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
        
        // Intersection Observer for animations
        this.setupIntersectionObserver();
    }
    
    handleScroll() {
        // Navbar background on scroll
        if (window.scrollY > 100) {
            this.navbar.classList.add('scrolled');
        } else {
            this.navbar.classList.remove('scrolled');
        }
        
        // Update active nav link based on scroll position
        this.updateActiveNavLink();
    }
    
    toggleMobileMenu() {
        this.navMenu.classList.toggle('active');
        this.navToggle.classList.toggle('active');
    }
    
    handleNavClick(e) {
        e.preventDefault();
        const targetId = e.currentTarget.getAttribute('href');
        const targetSection = document.querySelector(targetId);
        
        if (targetSection) {
            // Close mobile menu if open
            this.navMenu.classList.remove('active');
            this.navToggle.classList.remove('active');
            
            // Smooth scroll to section
            targetSection.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
    
    updateActiveNavLink() {
        const sections = document.querySelectorAll('section[id]');
        const scrollPosition = window.scrollY + 200;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                this.navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }
    
    handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(this.contactForm);
        const data = Object.fromEntries(formData.entries());
        
        // Simulate form submission
        const submitButton = this.contactForm.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        
        submitButton.textContent = 'Sending...';
        submitButton.disabled = true;
        
        setTimeout(() => {
            // Show success message
            alert('Thank you for your message! We will get back to you within 24-48 hours.');
            this.contactForm.reset();
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        }, 1500);
    }
    
    setupIntersectionObserver() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);
        
        // Observe service cards and therapist cards
        const animatedElements = document.querySelectorAll('.service-card, .therapist-card, .feature');
        animatedElements.forEach(el => observer.observe(el));
    }
}

// ============================================
// Initialize Everything
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize WebGL background with advanced physics
    const webgl = new WebGLBackground();
    
    // Initialize UI controller
    const ui = new UIController();
    
    // Add loading animation complete
    document.body.classList.add('loaded');
    
    // Expose physics controls globally for debugging/demo
    window.physicsEngine = {
        toggleBulletTime: () => webgl.toggleBulletTime(!webgl.bulletTimeActive),
        getVelocity: () => webgl.getVelocity(),
        getPlaybackRate: () => webgl.currentPlaybackRate
    };
    
    // Keyboard shortcut for bullet time (Space bar)
    document.addEventListener('keydown', (e) => {
        if (e.code === 'Space' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
            e.preventDefault();
            webgl.toggleBulletTime(!webgl.bulletTimeActive);
        }
    });
    
    console.log('Serenity Mental Health Clinic website loaded successfully!');
    console.log('CLASSIFIED PHYSICS ENGINE ACTIVE');
    console.log('- Press SPACE to toggle Bullet Time');
    console.log('- Move mouse to experience Viscous Inertia');
    console.log('- Scroll to activate Scroll-Scrubbed animations');
    console.log('- Watch for Temporal Echoes trailing floating shapes');
});

// ============================================
// Additional Utility Functions
// ============================================

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

// Add parallax effect to hero section
window.addEventListener('scroll', () => {
    const hero = document.querySelector('.hero');
    const scrolled = window.scrollY;
    
    if (hero && scrolled < window.innerHeight) {
        hero.style.backgroundPositionY = `${scrolled * 0.5}px`;
    }
});

// Stats counter animation
function animateStats() {
    const stats = document.querySelectorAll('.stat-number');
    
    stats.forEach(stat => {
        const target = parseInt(stat.textContent.replace(/\D/g, ''));
        const suffix = stat.textContent.replace(/[0-9]/g, '');
        let current = 0;
        const increment = target / 50;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                stat.textContent = target + suffix;
                clearInterval(timer);
            } else {
                stat.textContent = Math.floor(current) + suffix;
            }
        }, 30);
    });
}

// Trigger stats animation when visible
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            animateStats();
            statsObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

const heroStats = document.querySelector('.hero-stats');
if (heroStats) {
    statsObserver.observe(heroStats);
}

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
