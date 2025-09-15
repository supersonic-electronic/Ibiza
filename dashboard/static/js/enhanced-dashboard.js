/**
 * Enhanced Ibiza Dashboard - Bloomberg Inspired Interactive Features
 * Advanced Theme System with Persistent Storage and Dynamic Updates
 */

class IbizaDashboard {
    constructor() {
        this.currentTheme = localStorage.getItem('ibiza-theme') || 'midnight';
        this.currentSection = 'overview';
        this.isMobile = window.innerWidth <= 1024;
        this.sidebarOpen = false;
        
        this.init();
    }

    init() {
        this.setupThemeSystem();
        this.setupNavigation();
        this.setupMobileMenu();
        this.setupCodeBlocks();
        this.setupDiagrams();
        this.setupAnimations();
        this.setupResponsive();
        this.loadInitialState();
        
        console.log('🚀 Ibiza Dashboard Enhanced - Ready!');
    }

    /* ===============================================
       🎨 THEME SYSTEM
       =============================================== */

    setupThemeSystem() {
        // Apply saved theme
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        
        // Setup theme switcher
        const themeOptions = document.querySelectorAll('.theme-option');
        themeOptions.forEach(option => {
            option.addEventListener('click', (e) => {
                const theme = e.currentTarget.dataset.theme;
                this.switchTheme(theme);
            });
            
            // Mark active theme
            if (option.dataset.theme === this.currentTheme) {
                option.classList.add('active');
            }
        });

        // Add theme transition class to body
        document.body.classList.add('theme-transition');
    }

    switchTheme(themeName) {
        // Remove active class from all theme options
        document.querySelectorAll('.theme-option').forEach(option => {
            option.classList.remove('active');
        });

        // Add active class to selected theme
        const selectedOption = document.querySelector(`[data-theme="${themeName}"]`);
        if (selectedOption) {
            selectedOption.classList.add('active');
        }

        // Apply theme
        document.documentElement.setAttribute('data-theme', themeName);
        this.currentTheme = themeName;
        
        // Save to localStorage
        localStorage.setItem('ibiza-theme', themeName);

        // Animate theme change
        this.animateThemeChange();

        // Update any charts or dynamic content
        this.updateDynamicContent();

        console.log(`🎨 Theme switched to: ${themeName}`);
    }

    animateThemeChange() {
        const header = document.querySelector('.dashboard-header');
        if (header) {
            header.style.transform = 'scale(0.98)';
            setTimeout(() => {
                header.style.transform = 'scale(1)';
            }, 200);
        }
    }

    /* ===============================================
       🧭 NAVIGATION SYSTEM
       =============================================== */

    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        const sections = document.querySelectorAll('.content-section');

        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                // Only prevent default for internal navigation (links with data-section)
                // Allow external links (like Data Query) to work normally
                if (link.dataset.section) {
                    e.preventDefault();
                    const targetSection = link.dataset.section;
                    this.navigateToSection(targetSection);
                }
                // If no data-section, let the link work normally (follow href)
            });
        });
    }

    navigateToSection(sectionId) {
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        const activeNavLink = document.querySelector(`[data-section="${sectionId}"]`);
        if (activeNavLink) {
            activeNavLink.classList.add('active');
        }

        // Update sections with animation
        document.querySelectorAll('.content-section').forEach(section => {
            if (section.id === sectionId) {
                section.classList.add('active');
                section.style.animation = 'fadeInUp 0.6s ease-out';
            } else {
                section.classList.remove('active');
            }
        });

        this.currentSection = sectionId;
        
        // Close mobile menu if open
        if (this.isMobile && this.sidebarOpen) {
            this.closeMobileMenu();
        }

        // Scroll to top
        document.querySelector('.dashboard-main').scrollTop = 0;

        console.log(`📍 Navigated to section: ${sectionId}`);
    }

    /* ===============================================
       📱 MOBILE RESPONSIVE
       =============================================== */

    setupMobileMenu() {
        // Create mobile menu button if it doesn't exist
        if (this.isMobile && !document.querySelector('.mobile-menu-button')) {
            this.createMobileMenuButton();
        }

        const mobileButton = document.querySelector('.mobile-menu-button');
        const sidebar = document.querySelector('.dashboard-sidebar');
        
        if (mobileButton && sidebar) {
            mobileButton.addEventListener('click', () => {
                this.toggleMobileMenu();
            });

            // Close sidebar when clicking outside
            document.addEventListener('click', (e) => {
                if (this.sidebarOpen && 
                    !sidebar.contains(e.target) && 
                    !mobileButton.contains(e.target)) {
                    this.closeMobileMenu();
                }
            });
        }
    }

    createMobileMenuButton() {
        const button = document.createElement('button');
        button.className = 'mobile-menu-button';
        button.innerHTML = '<i class="fas fa-bars"></i>';
        button.setAttribute('aria-label', 'Toggle menu');
        document.body.appendChild(button);
    }

    toggleMobileMenu() {
        const sidebar = document.querySelector('.dashboard-sidebar');
        const button = document.querySelector('.mobile-menu-button');
        
        if (this.sidebarOpen) {
            this.closeMobileMenu();
        } else {
            sidebar.classList.add('open');
            button.innerHTML = '<i class="fas fa-times"></i>';
            this.sidebarOpen = true;
        }
    }

    closeMobileMenu() {
        const sidebar = document.querySelector('.dashboard-sidebar');
        const button = document.querySelector('.mobile-menu-button');
        
        sidebar.classList.remove('open');
        button.innerHTML = '<i class="fas fa-bars"></i>';
        this.sidebarOpen = false;
    }

    setupResponsive() {
        window.addEventListener('resize', () => {
            const wasMobile = this.isMobile;
            this.isMobile = window.innerWidth <= 1024;
            
            if (wasMobile !== this.isMobile) {
                if (this.isMobile && !document.querySelector('.mobile-menu-button')) {
                    this.createMobileMenuButton();
                } else if (!this.isMobile) {
                    const mobileButton = document.querySelector('.mobile-menu-button');
                    if (mobileButton) {
                        mobileButton.remove();
                    }
                    
                    const sidebar = document.querySelector('.dashboard-sidebar');
                    sidebar.classList.remove('open');
                    this.sidebarOpen = false;
                }
            }
        });
    }

    /* ===============================================
       💻 CODE BLOCK ENHANCEMENTS
       =============================================== */

    setupCodeBlocks() {
        // Setup copy functionality only - no syntax highlighting
        document.querySelectorAll('.code-block').forEach((block, index) => {
            this.setupCodeBlockCopy(block, index);
        });
    }

    setupCodeBlockCopy(codeBlock, index) {
        const container = codeBlock.parentNode;
        
        // Only setup copy functionality - no modification of content
        const copyButton = container.querySelector('.copy-button');
        if (copyButton) {
            copyButton.addEventListener('click', () => {
                this.copyCodeToClipboard(codeBlock, copyButton);
            });
        }

        // Add hover effects
        codeBlock.addEventListener('mouseenter', () => {
            codeBlock.style.borderColor = 'var(--primary-color)';
        });

        codeBlock.addEventListener('mouseleave', () => {
            codeBlock.style.borderColor = 'var(--border-color)';
        });
    }

    detectLanguage(code) {
        if (code.includes('from ') && code.includes('import ')) return 'Python';
        if (code.includes('npm ') || code.includes('yarn ')) return 'Shell';
        if (code.includes('function') && code.includes('{')) return 'JavaScript';
        if (code.includes('<') && code.includes('>')) return 'HTML';
        if (code.includes('def ') || code.includes('class ')) return 'Python';
        return 'Code';
    }

    applySyntaxHighlighting(codeBlock) {
        // Skip if already highlighted or if it contains HTML tags
        if (codeBlock.classList.contains('highlighted') || codeBlock.innerHTML.includes('<span')) {
            return;
        }

        const code = codeBlock.querySelector('code');
        if (!code) return;

        let text = code.textContent || code.innerText;
        
        // Clean Python syntax highlighting
        text = text.replace(/\b(from|import|def|class|if|else|elif|for|while|try|except|with|as|return|print|True|False|None)\b/g, 
            '<span style="color: #ff6b6b; font-weight: 600;">$1</span>');
        
        text = text.replace(/(["'])((?:\\.|(?!\1)[^\\])*)\1/g, 
            '<span style="color: #4ecdc4;">$1$2$1</span>');
        
        text = text.replace(/(#.*$)/gm, 
            '<span style="color: #95a5a6; font-style: italic;">$1</span>');
        
        text = text.replace(/\b(\d+(?:\.\d+)?)\b/g, 
            '<span style="color: #f39c12;">$1</span>');
        
        text = text.replace(/\b([a-zA-Z_][a-zA-Z0-9_]*)\(/g, 
            '<span style="color: #2ecc71;">$1</span>(');

        // Variables and attributes
        text = text.replace(/([a-zA-Z_][a-zA-Z0-9_]*)(\s*=)/g, 
            '<span style="color: #3498db;">$1</span>$2');

        code.innerHTML = text;
        codeBlock.classList.add('highlighted');
    }

    async copyCodeToClipboard(codeBlock, button) {
        const codeElement = codeBlock.querySelector('code');
        const text = codeElement ? codeElement.textContent : codeBlock.textContent;
        const originalContent = button.innerHTML;
        
        try {
            await navigator.clipboard.writeText(text);
            
            // Success feedback
            button.innerHTML = '<i class="fas fa-check"></i> Copied!';
            button.style.background = 'var(--success-color)';
            
            this.showNotification('Code copied to clipboard!', 'success');
            
            setTimeout(() => {
                button.innerHTML = originalContent;
                button.style.background = 'var(--primary-color)';
            }, 2000);
            
        } catch (err) {
            console.error('Failed to copy code:', err);
            
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            
            try {
                document.execCommand('copy');
                this.showNotification('Code copied to clipboard!', 'success');
            } catch (fallbackErr) {
                this.showNotification('Failed to copy code', 'error');
            }
            
            document.body.removeChild(textArea);
        }
    }

    /* ===============================================
       📊 DIAGRAM ENHANCEMENTS
       =============================================== */

    setupDiagrams() {
        const diagramTabs = document.querySelectorAll('.diagram-tab');
        const diagramContents = document.querySelectorAll('.diagram-content');

        diagramTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetDiagram = tab.dataset.diagram;
                this.showDiagram(targetDiagram);
            });
        });

        // Add zoom functionality to diagram images
        document.querySelectorAll('.diagram-img').forEach(img => {
            this.addImageZoom(img);
        });
    }

    showDiagram(diagramId) {
        // Update tabs
        document.querySelectorAll('.diagram-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        const activeTab = document.querySelector(`[data-diagram="${diagramId}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }

        // Update content with animation
        document.querySelectorAll('.diagram-content').forEach(content => {
            content.classList.remove('active');
        });

        const targetContent = document.getElementById(diagramId);
        if (targetContent) {
            setTimeout(() => {
                targetContent.classList.add('active');
            }, 150);
        }
    }

    addImageZoom(img) {
        img.style.cursor = 'zoom-in';
        
        img.addEventListener('click', () => {
            this.createImageModal(img);
        });
    }

    createImageModal(img) {
        const modal = document.createElement('div');
        modal.className = 'image-modal';
        modal.innerHTML = `
            <div class="modal-backdrop">
                <div class="modal-content">
                    <button class="modal-close">&times;</button>
                    <img src="${img.src}" alt="${img.alt}" class="modal-image">
                </div>
            </div>
        `;

        // Add styles
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 2000;
            background: rgba(0, 0, 0, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(10px);
        `;

        const modalImage = modal.querySelector('.modal-image');
        modalImage.style.cssText = `
            max-width: 90vw;
            max-height: 90vh;
            object-fit: contain;
            border-radius: var(--border-radius);
        `;

        const closeButton = modal.querySelector('.modal-close');
        closeButton.style.cssText = `
            position: absolute;
            top: 20px;
            right: 20px;
            background: var(--danger-color);
            color: white;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            font-size: 24px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        `;

        // Close modal functionality
        const closeModal = () => {
            modal.style.opacity = '0';
            setTimeout(() => document.body.removeChild(modal), 300);
        };

        closeButton.addEventListener('click', closeModal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });

        document.addEventListener('keydown', function escapeHandler(e) {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', escapeHandler);
            }
        });

        document.body.appendChild(modal);
        
        // Animate in
        modal.style.opacity = '0';
        setTimeout(() => modal.style.opacity = '1', 100);
    }

    /* ===============================================
       🎭 ANIMATIONS & EFFECTS
       =============================================== */

    setupAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in');
                }
            });
        }, observerOptions);

        // Observe cards for scroll animations
        document.querySelectorAll('.card').forEach(card => {
            observer.observe(card);
        });

        // Add floating animation to status badges (only on dashboard main content, exclude sidebar and status page)
        if (!window.location.pathname.includes('/status')) {
            document.querySelectorAll('.card .status-badge:not(.status-indicators .status-badge)').forEach((badge, index) => {
                badge.style.animationDelay = `${index * 0.1}s`;
                badge.classList.add('floating');
            });
        }

        // Progress bar animation
        this.animateProgress();
    }

    animateProgress() {
        const progressFill = document.querySelector('.progress-fill');
        if (progressFill) {
            progressFill.style.width = '0%';
            setTimeout(() => {
                progressFill.style.width = '45%';
            }, 500);
        }
    }

    /* ===============================================
       🔔 NOTIFICATION SYSTEM
       =============================================== */

    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        notification.innerHTML = `
            <i class="${icons[type] || icons.info}"></i>
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        `;

        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1500;
            background: var(--surface);
            color: var(--text-primary);
            border: 1px solid var(--${type === 'success' ? 'success' : type === 'error' ? 'danger' : type === 'warning' ? 'warning' : 'info'}-color);
            border-radius: var(--border-radius-sm);
            padding: 1rem 1.5rem;
            box-shadow: var(--shadow-lg);
            display: flex;
            align-items: center;
            gap: 0.75rem;
            max-width: 400px;
            font-weight: 500;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;

        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.style.cssText = `
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 1.2rem;
            cursor: pointer;
            margin-left: auto;
        `;

        closeBtn.addEventListener('click', () => {
            this.hideNotification(notification);
        });

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Auto hide
        setTimeout(() => {
            this.hideNotification(notification);
        }, duration);
    }

    hideNotification(notification) {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }

    /* ===============================================
       🔄 DYNAMIC CONTENT UPDATES
       =============================================== */

    updateDynamicContent() {
        // Update progress bars, charts, or any theme-dependent content
        this.updateProgressBars();
        this.updateChartColors();
        this.updateDiagramThemes();
    }

    updateProgressBars() {
        const progressBars = document.querySelectorAll('.progress-fill');
        progressBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.width = width;
            }, 300);
        });
    }

    updateChartColors() {
        // If Chart.js or other charting libraries are used, update their colors here
        console.log('📊 Chart colors updated for theme:', this.currentTheme);
    }

    updateDiagramThemes() {
        // Update diagram images to match current theme
        const diagramImages = document.querySelectorAll('.diagram-img');
        
        diagramImages.forEach(img => {
            const src = img.getAttribute('src');
            if (src && src.includes('/images/')) {
                // Extract diagram name from src
                const diagramName = src.split('/').pop().replace('.svg', '');
                const baseName = diagramName.replace(/_\w+$/, ''); // Remove existing theme suffix
                
                // Update src to use current theme
                const newSrc = src.replace(diagramName + '.svg', `${baseName}_${this.currentTheme}.svg`);
                
                // Fallback to default if theme-specific version doesn't exist
                const testImg = new Image();
                testImg.onload = () => {
                    img.src = newSrc;
                    img.style.opacity = '0';
                    setTimeout(() => {
                        img.style.opacity = '1';
                    }, 150);
                };
                testImg.onerror = () => {
                    // Keep original src if themed version doesn't exist
                    console.log(`Theme diagram not found: ${newSrc}, keeping default`);
                };
                testImg.src = newSrc;
            }
        });
        
        console.log('🎨 Diagrams updated for theme:', this.currentTheme);
    }

    /* ===============================================
       💾 STATE MANAGEMENT
       =============================================== */

    loadInitialState() {
        // Load saved section
        const savedSection = localStorage.getItem('ibiza-current-section');
        if (savedSection && document.getElementById(savedSection)) {
            this.navigateToSection(savedSection);
        }

        // Restore any other saved preferences
        this.restorePreferences();
    }

    saveState() {
        localStorage.setItem('ibiza-current-section', this.currentSection);
        localStorage.setItem('ibiza-theme', this.currentTheme);
    }

    restorePreferences() {
        // Restore any additional user preferences
        const preferences = localStorage.getItem('ibiza-preferences');
        if (preferences) {
            try {
                const prefs = JSON.parse(preferences);
                console.log('📂 Preferences restored:', prefs);
            } catch (e) {
                console.warn('Failed to parse preferences:', e);
            }
        }
    }

    /* ===============================================
       🔧 UTILITY FUNCTIONS
       =============================================== */

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Auto-save state periodically
    startAutoSave() {
        setInterval(() => {
            this.saveState();
        }, 30000); // Save every 30 seconds
    }
}

/* ===============================================
   🚀 INITIALIZATION
   =============================================== */

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new IbizaDashboard();
    
    // Make dashboard instance available globally for debugging
    window.IbizaDashboard = dashboard;
    
    // Start auto-save
    dashboard.startAutoSave();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Save state when page becomes hidden
        if (window.IbizaDashboard) {
            window.IbizaDashboard.saveState();
        }
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IbizaDashboard;
}