/**
 * Mental Health Clinic Website - Main JavaScript
 * Includes WebGL background animation with Three.js
 */

// ============================================
// WebGL Background Animation
// ============================================

class WebGLBackground {
    constructor() {
        this.canvas = document.getElementById('webgl-canvas');
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.particles = null;
        this.mouseX = 0;
        this.mouseY = 0;
        this.windowHalfX = window.innerWidth / 2;
        this.windowHalfY = window.innerHeight / 2;
        
        this.init();
        this.animate();
        this.addEventListeners();
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
        this.mouseX = event.clientX - this.windowHalfX;
        this.mouseY = event.clientY - this.windowHalfY;
    }
    
    onScroll() {
        const scrollY = window.scrollY;
        if (this.particles) {
            this.particles.rotation.y = scrollY * 0.0005;
            this.particles.rotation.x = scrollY * 0.0002;
        }
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        const time = Date.now() * 0.0001;
        
        // Animate particles
        if (this.particles) {
            this.particles.rotation.y += 0.001;
            this.particles.rotation.x += 0.0005;
            
            // Gentle mouse interaction
            this.particles.rotation.y += (this.mouseX * 0.0001 - this.particles.rotation.y) * 0.05;
            this.particles.rotation.x += (this.mouseY * 0.0001 - this.particles.rotation.x) * 0.05;
        }
        
        // Animate floating shapes
        if (this.floatingShapes) {
            this.floatingShapes.forEach((shape, index) => {
                shape.rotation.x += shape.userData.rotationSpeed.x;
                shape.rotation.y += shape.userData.rotationSpeed.y;
                
                // Floating motion
                shape.position.y += Math.sin(time * shape.userData.floatSpeed + shape.userData.floatOffset) * 0.5;
            });
        }
        
        this.renderer.render(this.scene, this.camera);
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
    // Initialize WebGL background
    const webgl = new WebGLBackground();
    
    // Initialize UI controller
    const ui = new UIController();
    
    // Add loading animation complete
    document.body.classList.add('loaded');
    
    console.log('Serenity Mental Health Clinic website loaded successfully!');
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
