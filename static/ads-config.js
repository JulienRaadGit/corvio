// Configuration des réseaux publicitaires
window.adsConfig = {
    // Google AdSense
    googleAdSense: {
        client: 'ca-pub-7173995370777543',
        enabled: true,
        adSlots: {
            header: 'header-ad',
            sidebar: 'sidebar-ad',
            footer: 'footer-ad',
            content: 'content-ad'
        }
    },
    
    // Awin
    awin: {
        enabled: true,
        publisherId: 'YOUR_AWIN_PUBLISHER_ID', // À remplacer par votre ID Awin
        trackingCode: 'YOUR_AWIN_TRACKING_CODE' // À remplacer par votre code de tracking
    },
    
    // Configuration générale
    settings: {
        // Délai avant affichage des publicités (en millisecondes)
        adDelay: 2000,
        
        // Nombre maximum de publicités par page
        maxAdsPerPage: 3,
        
        // Zones où les publicités sont autorisées
        allowedZones: ['header', 'sidebar', 'footer', 'content'],
        
        // Désactiver les publicités pour les utilisateurs connectés (optionnel)
        disableForLoggedUsers: false
    }
};

// Fonction pour charger les publicités
function loadAds() {
    if (!window.adsConfig) return;
    
    // Vérifier si l'utilisateur est connecté
    const isLoggedIn = document.querySelector('.user-profile') !== null;
    if (window.adsConfig.settings.disableForLoggedUsers && isLoggedIn) {
        return;
    }
    
    // Charger Google AdSense
    if (window.adsConfig.googleAdSense.enabled) {
        loadGoogleAdSense();
    }
    
    // Charger Awin
    if (window.adsConfig.awin.enabled) {
        loadAwin();
    }
}

// Fonction pour charger Google AdSense
function loadGoogleAdSense() {
    // Vérifier si AdSense est déjà chargé
    if (window.adsbygoogle) return;
    
    // Créer le script AdSense
    const script = document.createElement('script');
    script.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + window.adsConfig.googleAdSense.client;
    script.async = true;
    script.crossOrigin = 'anonymous';
    document.head.appendChild(script);
    
    // Initialiser les publicités après chargement
    script.onload = function() {
        (adsbygoogle = window.adsbygoogle || []).push({});
    };
}

// Fonction pour charger Awin
function loadAwin() {
    // Vérifier si Awin est déjà chargé
    if (window.awin) return;
    
    // Créer le script Awin
    const script = document.createElement('script');
    script.src = 'https://www.dwin1.com/' + window.adsConfig.awin.publisherId + '.js';
    script.async = true;
    document.head.appendChild(script);
}

// Fonction pour créer un emplacement publicitaire
function createAdSlot(zone, adType = 'banner') {
    const adContainer = document.createElement('div');
    adContainer.id = `ad-${zone}-${Date.now()}`;
    adContainer.className = 'ad-slot';
    adContainer.setAttribute('data-ad-zone', zone);
    adContainer.setAttribute('data-ad-type', adType);
    
    // Styles de base pour les emplacements publicitaires
    adContainer.style.cssText = `
        min-height: 90px;
        margin: 1rem 0;
        text-align: center;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--text-secondary);
        font-size: 0.9rem;
    `;
    
    // Contenu de placeholder
    adContainer.innerHTML = `
        <div>
            <i class="fas fa-ad" style="font-size: 2rem; color: var(--accent); margin-bottom: 0.5rem;"></i>
            <p>Publicité</p>
        </div>
    `;
    
    return adContainer;
}

// Fonction pour insérer une publicité dans une zone spécifique
function insertAd(zone, targetSelector, position = 'beforeend') {
    const target = document.querySelector(targetSelector);
    if (!target) return;
    
    const adSlot = createAdSlot(zone);
    
    if (position === 'beforebegin') {
        target.parentNode.insertBefore(adSlot, target);
    } else if (position === 'afterbegin') {
        target.insertBefore(adSlot, target.firstChild);
    } else if (position === 'beforeend') {
        target.appendChild(adSlot);
    } else if (position === 'afterend') {
        target.parentNode.insertBefore(adSlot, target.nextSibling);
    }
}

// Initialiser les publicités quand le DOM est chargé
document.addEventListener('DOMContentLoaded', function() {
    // Attendre un délai avant de charger les publicités
    setTimeout(loadAds, window.adsConfig?.settings?.adDelay || 2000);
    
    // Insérer des publicités dans des zones spécifiques
    if (window.adsConfig?.googleAdSense?.enabled) {
        // Publicité dans le header
        insertAd('header', '.hero-section', 'afterend');
        
        // Publicité dans le contenu
        insertAd('content', '.form-section', 'afterend');
        
        // Publicité dans le footer
        insertAd('footer', '.faq-section', 'afterend');
    }
});

// Fonction pour désactiver les publicités (pour les tests)
function disableAds() {
    const adSlots = document.querySelectorAll('.ad-slot');
    adSlots.forEach(slot => slot.remove());
}

// Fonction pour activer les publicités
function enableAds() {
    loadAds();
} 