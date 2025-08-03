// Script de test pour le menu burger mobile
console.log('=== MOBILE MENU TEST SCRIPT LOADED ===');

// Attendre que le DOM soit chargé
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded in test script');
    
    // Vérifier les éléments
    const toggleButton = document.querySelector('.nav-toggle');
    const mobileMenu = document.querySelector('.nav-menu.mobile-menu');
    const overlay = document.querySelector('.nav-overlay');
    
    console.log('Elements found:');
    console.log('- Toggle button:', toggleButton);
    console.log('- Mobile menu:', mobileMenu);
    console.log('- Overlay:', overlay);
    
    if (toggleButton) {
        console.log('Toggle button classes:', toggleButton.className);
        console.log('Toggle button HTML:', toggleButton.outerHTML);
        
        // Ajouter un event listener de test
        toggleButton.addEventListener('click', function(e) {
            console.log('=== TOGGLE BUTTON CLICKED ===');
            e.preventDefault();
            e.stopPropagation();
            
            // Toggle les classes
            toggleButton.classList.toggle('active');
            if (mobileMenu) mobileMenu.classList.toggle('active');
            if (overlay) overlay.classList.toggle('active');
            
            console.log('Classes after toggle:');
            console.log('- Toggle button active:', toggleButton.classList.contains('active'));
            console.log('- Mobile menu active:', mobileMenu ? mobileMenu.classList.contains('active') : 'N/A');
            console.log('- Overlay active:', overlay ? overlay.classList.contains('active') : 'N/A');
        });
        
        console.log('Test event listener added to toggle button');
    } else {
        console.error('Toggle button not found!');
    }
    
    // Vérifier les styles CSS
    const computedStyle = window.getComputedStyle(toggleButton);
    console.log('Toggle button display:', computedStyle.display);
    console.log('Toggle button visibility:', computedStyle.visibility);
    
    // Vérifier la largeur de l'écran
    console.log('Window width:', window.innerWidth);
    console.log('Is mobile view (< 768px):', window.innerWidth < 768);
});

// Ajouter un event listener global pour capturer tous les clics
document.addEventListener('click', function(e) {
    if (e.target.closest('.nav-toggle')) {
        console.log('Click detected on nav-toggle or its children');
    }
}); 