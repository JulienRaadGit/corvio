// Configuration des réseaux publicitaires
window.adsConfig = {
    // Google AdSense
    googleAdSense: {
        client: 'ca-pub-7173995370777543',
        enabled: true
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

// Initialiser les publicités quand le DOM est chargé
document.addEventListener('DOMContentLoaded', function() {
    // Attendre un délai avant de charger les publicités
    setTimeout(loadAds, window.adsConfig?.settings?.adDelay || 2000);
});

// Fonction pour désactiver les publicités (pour les tests)
function disableAds() {
    // Supprimer les scripts AdSense
    const adScripts = document.querySelectorAll('script[src*="googlesyndication"]');
    adScripts.forEach(script => script.remove());
}

// Fonction pour activer les publicités
function enableAds() {
    loadAds();
} 