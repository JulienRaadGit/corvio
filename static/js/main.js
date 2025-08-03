document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded - Initializing mobile menu functionality');
    
    const form = document.getElementById('infoForm');
    const resultSection = document.getElementById('resultSection');
    const programContainer = document.getElementById('programContainer');
    const productList = document.getElementById('productList');
    const exerciseListDiv = document.getElementById('exerciseList');
    const loadingSpinner = document.getElementById('loadingSpinner');

    // Firebase Authentication
    // Import Firebase modules
    import('https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js').then(({ initializeApp }) => {
        return import('https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js').then(({ getAuth, onAuthStateChanged, signOut }) => {
            // Firebase configuration
            const firebaseConfig = {
                apiKey: "AIzaSyA_CrBjnDmhDfvvTmx6coTozdyChQMQdjE",
                authDomain: "corvio-bf0b0.firebaseapp.com",
                projectId: "corvio-bf0b0",
                storageBucket: "corvio-bf0b0.firebasestorage.app",
                messagingSenderId: "637844838567",
                appId: "1:637844838567:web:d8cabed8e8107426642382",
                measurementId: "G-D807BNWELB"
            };

            // Initialize Firebase
            const app = initializeApp(firebaseConfig);
            const auth = getAuth(app);

            // Handle logout
            const logoutBtn = document.querySelector('.btn-logout');
            if (logoutBtn) {
                logoutBtn.addEventListener('click', async (e) => {
                    e.preventDefault();
                    try {
                        await signOut(auth);
                        window.location.href = '/logout';
                    } catch (error) {
                        console.error('Error signing out:', error);
                        window.location.href = '/logout';
                    }
                });
            }

            // Auth state observer with persistent session
            onAuthStateChanged(auth, async (user) => {
                if (user) {
                    console.log('User is signed in:', user.email);
                    // Automatically refresh session on page load
                    try {
                        const idToken = await user.getIdToken(true); // Force refresh
                        await fetch('/verify-token', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                idToken: idToken
                            })
                        });
                        console.log('Session refreshed successfully');
                    } catch (error) {
                        console.error('Error refreshing session:', error);
                    }
                } else {
                    console.log('User is signed out');
                }
            });

            // Check authentication status on page load
            checkAuthStatus();
        });
    }).catch(error => {
        console.error('Error loading Firebase:', error);
    });

    // Function to check authentication status
    async function checkAuthStatus() {
        try {
            const response = await fetch('/check-auth');
            const data = await response.json();
            
            if (data.authenticated) {
                console.log('User is authenticated:', data.user);
                // Update UI to show authenticated state
                updateAuthUI(true, data.user);
            } else {
                console.log('User is not authenticated');
                updateAuthUI(false);
            }
        } catch (error) {
            console.error('Error checking auth status:', error);
        }
    }

    // Function to update UI based on authentication status
    function updateAuthUI(isAuthenticated, user = null) {
        const authElements = document.querySelectorAll('.auth-required');
        const guestElements = document.querySelectorAll('.guest-only');
        
        if (isAuthenticated) {
            // Show authenticated content
            authElements.forEach(el => el.style.display = 'block');
            guestElements.forEach(el => el.style.display = 'none');
            
            // Update user info if available
            if (user) {
                const userNameElements = document.querySelectorAll('.user-name');
                userNameElements.forEach(el => {
                    el.textContent = user.name || user.email;
                });
            }
        } else {
            // Show guest content
            authElements.forEach(el => el.style.display = 'none');
            guestElements.forEach(el => el.style.display = 'block');
        }
    }

    // Fonction pour afficher les exercices
    function renderExercises(exercises) {
        if (!exerciseListDiv) return;
        
        exerciseListDiv.innerHTML = '';
        exercises.forEach(item => {
            const container = document.createElement('div');
            container.classList.add('exercise-item');
            // Chemin de l'image: static/images/exercises/{image}
            const img = document.createElement('img');
            if (item.image) {
                img.src = `/static/images/exercises/${item.image}`;
                img.alt = item.name;
            } else {
                // image par défaut si aucune image n'est fournie
                img.src = '/static/images/placeholder.jpg';
                img.alt = 'Image en attente';
            }
            const name = document.createElement('p');
            name.textContent = item.name;
            container.appendChild(img);
            container.appendChild(name);
            exerciseListDiv.appendChild(container);
        });
    }

    // Gérer l'affichage des options d'équipement selon le choix de la salle de sport
    const gymYesRadio = document.getElementById('gymYes');
    const gymNoRadio = document.getElementById('gymNo');
    const equipmentOptionsDiv = document.getElementById('equipmentOptions');

    function toggleEquipmentOptions() {
        if (equipmentOptionsDiv) {
            if (gymNoRadio && gymNoRadio.checked) {
                equipmentOptionsDiv.style.display = 'block';
            } else {
                equipmentOptionsDiv.style.display = 'none';
            }
        }
    }

    // Ajoute des écouteurs pour changer l'affichage
    if (gymYesRadio) {
        gymYesRadio.addEventListener('change', toggleEquipmentOptions);
    }
    if (gymNoRadio) {
        gymNoRadio.addEventListener('change', toggleEquipmentOptions);
    }

    // Afficher correctement lors du chargement initial
    toggleEquipmentOptions();

    // Récupérer la liste des exercices au chargement
    // Variable pour stocker la liste des exercices disponibles
    let exerciseData = [];

    fetch('/static/data/exercises.json')
        .then(response => response.json())
        .then(data => {
            exerciseData = data;
            renderExercises(data);
        })
        .catch(err => {
            console.error('Erreur lors du chargement des exercices:', err);
        });

    // Gestionnaire pour le formulaire
    if (form) {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            // Récupérer les valeurs du formulaire
            const age = document.getElementById('age').value;
            const height = document.getElementById('height').value;
            const weight = document.getElementById('weight').value;
            const difficulty = document.getElementById('difficulty').value;
            const maxSessionDuration = document.getElementById('maxSessionDuration').value || null;
            const maxWorkoutDays = document.getElementById('maxWorkoutDays').value || null;
            
            // Déterminer si l'utilisateur est en salle de sport
            const gym = gymYesRadio ? gymYesRadio.checked : false;
            // Récupérer la liste des équipements sélectionnés si pas en salle de sport
            let equipmentList = [];
            if (!gym) {
                const checkboxes = document.querySelectorAll('input[name="equipmentList"]:checked');
                equipmentList = Array.from(checkboxes).map(cb => cb.value);
            }

            // Reset l'affichage
            if (programContainer) {
                programContainer.innerHTML = '<p>Génération en cours…</p>';
            }
            if (productList) {
                productList.innerHTML = '';
            }
            if (resultSection) {
                resultSection.style.display = 'block';
            }
            // Show loading spinner, hide results
            if (loadingSpinner) loadingSpinner.style.display = 'flex';
            if (resultSection) {
                resultSection.classList.remove('visible');
            }
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        age: age,
                        height: height,
                        weight: weight,
                        difficulty: difficulty,
                        maxSessionDuration: maxSessionDuration,
                        maxWorkoutDays: maxWorkoutDays,
                        gym: gym,
                        equipmentList: equipmentList
                    })
                });
                
                if (response.status === 401) {
                    // Rediriger vers la page de connexion si non authentifié
                    window.location.href = '/login';
                    return;
                }
                
                const data = await response.json();
                // Essayer d'interpréter la réponse comme JSON structuré
                let schedule;
                try {
                    schedule = JSON.parse(data.plan);
                } catch (e) {
                    // Si ce n'est pas un JSON valide, afficher le texte brut
                    if (programContainer) {
                        programContainer.textContent = data.plan;
                    }
                    schedule = null;
                }
                if (schedule && programContainer) {
                    renderSchedule(schedule);
                }
                // Afficher les produits
                if (data.products && productList) {
                    data.products.forEach(prod => {
                        const productCard = document.createElement('div');
                        productCard.classList.add('product-card');
                        
                        const productName = document.createElement('h4');
                        productName.textContent = prod.name;
                        
                        const productDesc = document.createElement('p');
                        productDesc.textContent = prod.description;
                        
                        const productLink = document.createElement('a');
                        productLink.href = prod.link || '#';
                        productLink.target = '_blank';
                        productLink.rel = 'noopener noreferrer';
                        productLink.textContent = 'Voir le produit';
                        productLink.innerHTML += ' <i class="fas fa-external-link-alt"></i>';
                        
                        productCard.appendChild(productName);
                        productCard.appendChild(productDesc);
                        productCard.appendChild(productLink);
                        productList.appendChild(productCard);
                    });
                }
                // Hide spinner, fade in results
                if (loadingSpinner) loadingSpinner.style.display = 'none';
                if (resultSection) {
                    setTimeout(() => {
                        resultSection.classList.add('visible');
                    }, 100);
                }
            } catch (error) {
                if (programContainer) {
                    programContainer.textContent = 'Une erreur est survenue lors de la génération du programme.';
                }
                if (loadingSpinner) loadingSpinner.style.display = 'none';
                if (resultSection) {
                    resultSection.classList.add('visible');
                }
                console.error(error);
            }
        });
    }

    /**
     * Affiche le programme structuré sous forme d'agenda interactif.
     * @param {Object} schedule - Objet JSON avec un tableau 'jours'.
     */
    function renderSchedule(schedule) {
        if (!programContainer) return;
        
        programContainer.innerHTML = '';
        if (!schedule || !Array.isArray(schedule.jours)) {
            programContainer.textContent = 'Format de programme inattendu.';
            return;
        }
        
        // Pour chaque jour, créer une carte
        schedule.jours.forEach((dayObj, dayIndex) => {
            const card = document.createElement('div');
            card.classList.add('day-card');
            
            // Ajouter la classe pour les jours de repos
            if (dayObj.type === 'rest') {
                card.classList.add('rest-day');
            } else {
                card.classList.add('workout-day');
            }
            
            const title = document.createElement('h4');
            title.textContent = dayObj.nomJour || `Jour ${dayIndex + 1}`;
            card.appendChild(title);
            
            // Contenu selon le type de jour
            if (dayObj.type === 'rest') {
                const restContent = document.createElement('div');
                restContent.classList.add('rest-content');
                
                const restIcon = document.createElement('span');
                restIcon.classList.add('rest-icon');
                restIcon.textContent = '😴';
                
                const restText = document.createElement('p');
                restText.textContent = 'Jour de repos';
                
                const restSubtext = document.createElement('small');
                restSubtext.textContent = 'Profitez de votre récupération !';
                
                restContent.appendChild(restIcon);
                restContent.appendChild(restText);
                restContent.appendChild(restSubtext);
                card.appendChild(restContent);
            } else {
                // Liste des exercices pour les jours d'entraînement
                if (Array.isArray(dayObj.exercices)) {
                    const exercisesList = document.createElement('div');
                    exercisesList.classList.add('exercises-list');
                    
                    dayObj.exercices.forEach((exercise, exIndex) => {
                        const exerciseItem = document.createElement('div');
                        exerciseItem.classList.add('exercise-item');
                        
                        const exerciseHeader = document.createElement('div');
                        exerciseHeader.classList.add('exercise-header');
                        
                        const exerciseName = document.createElement('h5');
                        exerciseName.textContent = exercise.nom || `Exercice ${exIndex + 1}`;
                        
                        const exerciseType = document.createElement('span');
                        exerciseType.classList.add('exercise-type');
                        
                        // Déterminer si l'exercice est mesuré en temps ou répétitions
                        const timeBasedExercises = [4, 16, 20, 21, 22, 23, 24, 30]; // IDs des exercices en temps
                        const exerciseId = exercise.id || exercise.nom_id;
                        
                        if (exercise.duree_minutes || (exerciseId && timeBasedExercises.includes(exerciseId))) {
                            // Exercice mesuré en temps
                            const duration = exercise.duree_minutes || exercise.minutes || 1;
                            exerciseType.textContent = `${exercise.series} séries × ${duration} min`;
                            exerciseType.classList.add('time-based');
                        } else if (exercise.repetitions) {
                            // Exercice mesuré en répétitions
                            exerciseType.textContent = `${exercise.series} séries × ${exercise.repetitions} répétitions`;
                            exerciseType.classList.add('repetition-based');
                        } else {
                            exerciseType.textContent = `${exercise.series} séries`;
                        }
                        
                        exerciseHeader.appendChild(exerciseName);
                        exerciseHeader.appendChild(exerciseType);
                        exerciseItem.appendChild(exerciseHeader);
                        exercisesList.appendChild(exerciseItem);
                    });
                    
                    card.appendChild(exercisesList);
                }
            }
            
            programContainer.appendChild(card);
        });
    }

    // Mobile Menu Functionality
    console.log('Setting up mobile menu functionality...');
    const toggleButton = document.querySelector('.nav-toggle');
    const mobileMenu = document.querySelector('.nav-menu.mobile-menu');
    const overlay = document.querySelector('.nav-overlay');
    
    console.log('Toggle button found:', !!toggleButton);
    console.log('Mobile menu found:', !!mobileMenu);
    console.log('Overlay found:', !!overlay);
    
    if (toggleButton && mobileMenu && overlay) {
        console.log('All mobile menu elements found, setting up event listeners...');
        
        // Toggle mobile menu
        toggleButton.addEventListener('click', (e) => {
            console.log('Toggle button clicked!');
            e.preventDefault();
            e.stopPropagation();
            
            toggleButton.classList.toggle('active');
            mobileMenu.classList.toggle('active');
            overlay.classList.toggle('active');
            
            console.log('Menu toggled - Active state:', mobileMenu.classList.contains('active'));
            
            // Prevent body scroll when menu is open
            if (mobileMenu.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });
        
        // Close menu when clicking overlay
        overlay.addEventListener('click', () => {
            console.log('Overlay clicked, closing menu');
            toggleButton.classList.remove('active');
            mobileMenu.classList.remove('active');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        });
        
        // Close menu when clicking a link
        const navLinks = mobileMenu.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                console.log('Nav link clicked, closing menu');
                toggleButton.classList.remove('active');
                mobileMenu.classList.remove('active');
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            });
        });
        
        // Close menu with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && mobileMenu.classList.contains('active')) {
                console.log('Escape key pressed, closing menu');
                toggleButton.classList.remove('active');
                mobileMenu.classList.remove('active');
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
        
        console.log('Mobile menu event listeners attached successfully');
    } else {
        console.error('Mobile menu elements not found:');
        console.error('- Toggle button:', !!toggleButton);
        console.error('- Mobile menu:', !!mobileMenu);
        console.error('- Overlay:', !!overlay);
    }
    
    // Handle window resize
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            // Reset menu on large screens
            if (toggleButton) toggleButton.classList.remove('active');
            if (mobileMenu) mobileMenu.classList.remove('active');
            if (overlay) overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
    
    console.log('Mobile menu setup complete');
});