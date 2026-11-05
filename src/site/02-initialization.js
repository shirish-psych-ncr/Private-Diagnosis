import { WebGLBackground } from './00-preamble.js';
import { UIController } from './01-interactions.js';
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

