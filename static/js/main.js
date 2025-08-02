document.addEventListener('DOMContentLoaded', () => {
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

            // Auth state observer
            onAuthStateChanged(auth, (user) => {
                if (user) {
                    console.log('User is signed in:', user.email);
                } else {
                    console.log('User is signed out');
                }
            });
        });
    }).catch(error => {
        console.error('Error loading Firebase:', error);
    });

    // Fonction pour afficher les exercices
    function renderExercises(exercises) {
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
        if (gymNoRadio.checked) {
            equipmentOptionsDiv.style.display = 'block';
        } else {
            equipmentOptionsDiv.style.display = 'none';
        }
    }

    // Ajoute des écouteurs pour changer l'affichage
    gymYesRadio.addEventListener('change', toggleEquipmentOptions);
    gymNoRadio.addEventListener('change', toggleEquipmentOptions);

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
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        // Récupérer les valeurs du formulaire
        const age = document.getElementById('age').value;
        const height = document.getElementById('height').value;
        const weight = document.getElementById('weight').value;
        // Déterminer si l'utilisateur est en salle de sport
        const gym = gymYesRadio.checked;
        // Récupérer la liste des équipements sélectionnés si pas en salle de sport
        let equipmentList = [];
        if (!gym) {
            const checkboxes = document.querySelectorAll('input[name="equipmentList"]:checked');
            equipmentList = Array.from(checkboxes).map(cb => cb.value);
        }

        // Reset l'affichage
        programContainer.innerHTML = '<p>Génération en cours…</p>';
        productList.innerHTML = '';
        resultSection.style.display = 'block';
        // Show loading spinner, hide results
        if (loadingSpinner) loadingSpinner.style.display = 'flex';
        resultSection.classList.remove('visible');
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
                programContainer.textContent = data.plan;
                schedule = null;
            }
            if (schedule) {
                renderSchedule(schedule);
            }
            // Afficher les produits
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
            // Hide spinner, fade in results
            if (loadingSpinner) loadingSpinner.style.display = 'none';
            setTimeout(() => {
                resultSection.classList.add('visible');
            }, 100);
        } catch (error) {
            programContainer.textContent = 'Une erreur est survenue lors de la génération du programme.';
            if (loadingSpinner) loadingSpinner.style.display = 'none';
            resultSection.classList.add('visible');
            console.error(error);
        }
    });

    /**
     * Affiche le programme structuré sous forme d'agenda interactif.
     * @param {Object} schedule - Objet JSON avec un tableau 'jours'.
     */
    function renderSchedule(schedule) {
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

    // Ajouter les contrôles d'édition après avoir rendu le programme
    // Note: Les boutons d'édition ne sont ajoutés que dans la page "Mes Workouts"
    // Pas lors de la génération initiale

    // Ajouter les contrôles d'édition après avoir rendu le programme
    // Cette fonction n'est utilisée que dans la page "Mes Workouts"
function addEditControls() {
    // Vérifier si nous sommes dans la page "Mes Workouts" (workout_plan.html)
    const isWorkoutPlanPage = window.location.pathname === '/workout-plan';
    
    if (!isWorkoutPlanPage) {
        return; // Ne pas ajouter les contrôles d'édition sur la page d'accueil
    }
    
    // Ajouter les boutons d'édition aux exercices
    document.querySelectorAll('.exercise-item').forEach(item => {
        if (!item.querySelector('.exercise-actions')) {
            const actionsHTML = `
                <div class="exercise-actions">
                    <button class="btn-edit">Modifier</button>
                    <button class="btn-delete">Supprimer</button>
                </div>
                <div class="exercise-edit-form">
                    <div class="edit-form-grid">
                        <div class="edit-form-group">
                            <label>Nom de l'exercice</label>
                            <input type="text" name="exercise-name" required>
                        </div>
                        <div class="edit-form-group">
                            <label>Séries</label>
                            <input type="number" name="series" min="1" required>
                        </div>
                        <div class="edit-form-group">
                            <label>Répétitions</label>
                            <input type="number" name="repetitions" min="1">
                        </div>
                    </div>
                    <div class="edit-form-group">
                        <label>Durée (minutes) - si pas de répétitions</label>
                        <input type="number" name="duration" min="1">
                    </div>
                    <div class="edit-form-actions">
                        <button class="btn btn-success btn-small btn-save-exercise">Sauvegarder</button>
                        <button class="btn btn-cancel btn-small btn-cancel-edit">Annuler</button>
                    </div>
                </div>
            `;
            item.insertAdjacentHTML('beforeend', actionsHTML);
        }
    });
    
    // Ajouter des boutons "Ajouter exercice" aux jours d'entraînement
    document.querySelectorAll('.day-card.workout-day').forEach(dayCard => {
        if (!dayCard.querySelector('.add-exercise-btn')) {
            const exercisesList = dayCard.querySelector('.exercises-list');
            if (exercisesList) {
                exercisesList.insertAdjacentHTML('afterend', '<button class="add-exercise-btn">+ Ajouter un exercice</button>');
            }
        }
    });
    
    // Initialiser l'éditeur si disponible
    if (typeof WorkoutEditor !== 'undefined') {
        window.workoutEditor = new WorkoutEditor();
        window.workoutEditor.workoutPlan = JSON.parse(plan);
        window.workoutEditor.renderEditablePlan();
    }
}
})
// Code à ajouter à la fin du fichier main.js

// Mobile Menu Functionality
document.addEventListener('DOMContentLoaded', () => {
    const toggleButton = document.querySelector('.nav-toggle');
    const mobileMenu = document.querySelector('.nav-menu.mobile-menu');
    const overlay = document.querySelector('.nav-overlay');
    
    if (toggleButton && mobileMenu && overlay) {
        // Toggle mobile menu
        toggleButton.addEventListener('click', () => {
            toggleButton.classList.toggle('active');
            mobileMenu.classList.toggle('active');
            overlay.classList.toggle('active');
            
            // Prevent body scroll when menu is open
            if (mobileMenu.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });
        
        // Close menu when clicking overlay
        overlay.addEventListener('click', () => {
            toggleButton.classList.remove('active');
            mobileMenu.classList.remove('active');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        });
        
        // Close menu when clicking a link
        const navLinks = mobileMenu.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                toggleButton.classList.remove('active');
                mobileMenu.classList.remove('active');
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            });
        });
        
        // Close menu with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && mobileMenu.classList.contains('active')) {
                toggleButton.classList.remove('active');
                mobileMenu.classList.remove('active');
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
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
});