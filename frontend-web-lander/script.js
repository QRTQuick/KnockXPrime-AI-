// Initialize AOS (Animate On Scroll)
AOS.init({
    duration: 800,
    easing: 'ease-in-out',
    once: true,
    offset: 100
});

// Mobile Navigation Toggle
const navToggle = document.getElementById('nav-toggle');
const navMenu = document.getElementById('nav-menu');

navToggle.addEventListener('click', () => {
    navMenu.classList.toggle('active');
    navToggle.classList.toggle('active');
});

// Close mobile menu when clicking on a link
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
        navMenu.classList.remove('active');
        navToggle.classList.remove('active');
    });
});

// Smooth scrolling for navigation links
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Navbar scroll effect
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.background = 'rgba(255, 255, 255, 0.98)';
        navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.background = 'rgba(255, 255, 255, 0.95)';
        navbar.style.boxShadow = 'none';
    }
});

// Typing animation for code example
const codeElement = document.querySelector('.code-content code');
if (codeElement) {
    const codeText = codeElement.textContent;
    codeElement.textContent = '';
    
    let i = 0;
    const typeWriter = () => {
        if (i < codeText.length) {
            codeElement.textContent += codeText.charAt(i);
            i++;
            setTimeout(typeWriter, 20);
        }
    };
    
    // Start typing animation when code section is in view
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                setTimeout(typeWriter, 500);
                observer.unobserve(entry.target);
            }
        });
    });
    
    observer.observe(codeElement);
}

// Pricing card interactions
document.querySelectorAll('.pricing-card .btn').forEach(button => {
    button.addEventListener('click', (e) => {
        e.preventDefault();
        const planName = e.target.closest('.pricing-card').querySelector('.plan-name').textContent;
        
        // Simulate plan selection
        alert(`You selected the ${planName} plan! Redirecting to signup...`);
        
        // In a real application, you would redirect to your signup/payment page
        // window.location.href = `/signup?plan=${planName.toLowerCase().replace(' ', '-')}`;
    });
});

// Feature card hover effects
document.querySelectorAll('.feature-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
        card.style.transform = 'translateY(-10px) scale(1.02)';
    });
    
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'translateY(0) scale(1)';
    });
});

// Parallax effect for floating elements
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const parallaxElements = document.querySelectorAll('.float-element');
    
    parallaxElements.forEach((element, index) => {
        const speed = 0.5 + (index * 0.1);
        element.style.transform = `translateY(${scrolled * speed}px)`;
    });
});

// Counter animation for hero stats
function animateCounters() {
    const counters = document.querySelectorAll('.stat-number');
    
    counters.forEach(counter => {
        const target = counter.textContent;
        const numericTarget = parseInt(target.replace(/[^\d]/g, ''));
        const suffix = target.replace(/[\d]/g, '');
        
        let current = 0;
        const increment = numericTarget / 100;
        
        const updateCounter = () => {
            if (current < numericTarget) {
                current += increment;
                counter.textContent = Math.floor(current) + suffix;
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target;
            }
        };
        
        updateCounter();
    });
}

// Trigger counter animation when hero section is in view
const heroObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            setTimeout(animateCounters, 1000);
            heroObserver.unobserve(entry.target);
        }
    });
});

const heroSection = document.querySelector('.hero');
if (heroSection) {
    heroObserver.observe(heroSection);
}

// Add loading animation
window.addEventListener('load', () => {
    document.body.classList.add('loaded');
});

// Easter egg: Konami code
let konamiCode = [];
const konamiSequence = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65];

document.addEventListener('keydown', (e) => {
    konamiCode.push(e.keyCode);
    
    if (konamiCode.length > konamiSequence.length) {
        konamiCode.shift();
    }
    
    if (konamiCode.join(',') === konamiSequence.join(',')) {
        // Easter egg activated!
        document.body.style.animation = 'rainbow 2s infinite';
        setTimeout(() => {
            document.body.style.animation = '';
        }, 5000);
        
        // Show special message
        const message = document.createElement('div');
        message.innerHTML = '🎉 KnockXPrime AI Developer Mode Activated! 🎉';
        message.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
            color: white;
            padding: 20px;
            border-radius: 10px;
            font-weight: bold;
            z-index: 10000;
            animation: bounce 1s infinite;
        `;
        
        document.body.appendChild(message);
        
        setTimeout(() => {
            document.body.removeChild(message);
        }, 3000);
        
        konamiCode = [];
    }
});

// Add rainbow animation for easter egg
const style = document.createElement('style');
style.textContent = `
    @keyframes rainbow {
        0% { filter: hue-rotate(0deg); }
        100% { filter: hue-rotate(360deg); }
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translate(-50%, -50%) translateY(0); }
        40% { transform: translate(-50%, -50%) translateY(-30px); }
        60% { transform: translate(-50%, -50%) translateY(-15px); }
    }
`;
document.head.appendChild(style);