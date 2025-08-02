class WorkoutEditor {
    constructor() {
        this.workoutPlan = null;
        this.isModified = false;
        this.init();
    }

    init() {
        // Récupérer le plan depuis le DOM s'il existe
        this.loadWorkoutPlan();
        this.bindEvents();
    }

    loadWorkoutPlan() {
        // Essayer de récupérer le plan depuis une variable globale ou le DOM
        if (window.workoutPlanData) {
            this.workoutPlan = window.workoutPlanData;
            this.renderEditablePlan();
        }
    }

    bindEvents() {
        // Écouter les clics sur les boutons d'édition
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-edit')) {
                this.editExercise(e.target);
            } else if (e.target.classList.contains('btn-delete')) {
                this.deleteExercise(e.target);
            } else if (e.target.classList.contains('add-exercise-btn')) {
                this.addExercise(e.target);
            } else if (e.target.classList.contains('btn-save-exercise')) {
                this.saveExercise(e.target);
            } else if (e.target.classList.contains('btn-cancel-edit')) {
                this.cancelEdit(e.target);
            } else if (e.target.classList.contains('btn-save-new-exercise')) {
                this.saveNewExercise(e.target);
            } else if (e.target.classList.contains('btn-cancel-add')) {
                this.cancelAdd(e.target);
            }
        });

        // Écouter les changements de sélection d'exercices
        document.addEventListener('change', (e) => {
            if (e.target.name === 'exercise-select' || e.target.name === 'new-exercise-select') {
                this.handleExerciseSelection(e.target);
            }
        });

        // Gestion des interactions tactiles pour mobile
        this.setupTouchInteractions();

        // Sauvegarder automatiquement quand le plan est modifié
        document.addEventListener('plan-modified', () => {
            this.savePlan();
        });

        // Charger la liste des exercices
        this.loadExercisesList();
    }

    setupTouchInteractions() {
        // Détecter si l'appareil supporte le toucher
        const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        
        if (isTouchDevice) {
            // Ajouter des classes pour les appareils tactiles
            document.body.classList.add('touch-device');
            
            // Gérer les interactions tactiles sur les exercices
            document.addEventListener('touchstart', (e) => {
                const exerciseItem = e.target.closest('.exercise-item');
                if (exerciseItem && !e.target.closest('.exercise-actions')) {
                    // Ajouter un effet visuel au toucher
                    exerciseItem.classList.add('touch-active');
                }
            }, { passive: true });

            document.addEventListener('touchend', (e) => {
                const exerciseItem = e.target.closest('.exercise-item');
                if (exerciseItem) {
                    // Retirer l'effet visuel
                    setTimeout(() => {
                        exerciseItem.classList.remove('touch-active');
                    }, 150);
                }
            }, { passive: true });
        }
    }

    editExercise(button) {
        const exerciseItem = button.closest('.exercise-item');
        const editForm = exerciseItem.querySelector('.exercise-edit-form');
        
        if (editForm) {
            exerciseItem.classList.add('editing');
            editForm.classList.add('active');
            
            // Pré-remplir le formulaire avec les valeurs actuelles
            const exerciseName = exerciseItem.querySelector('h5').textContent;
            const exerciseType = exerciseItem.querySelector('.exercise-type').textContent;
            
            // Parser les informations actuelles
            const exerciseSelect = editForm.querySelector('select[name="exercise-select"]');
            const seriesInput = editForm.querySelector('input[name="series"]');
            const repsInput = editForm.querySelector('input[name="repetitions"]');
            const durationInput = editForm.querySelector('input[name="duration"]');
            
            // Trouver l'exercice dans la liste et sélectionner le bon
            const exercise = this.exercisesList.find(ex => ex.name === exerciseName);
            if (exercise) {
                exerciseSelect.value = exercise.id;
                this.handleExerciseSelection(exerciseSelect);
            }
            
            // Parser le type d'exercice pour extraire séries/répétitions/durée
            const match = exerciseType.match(/(\d+)\s*(?:sets|séries)\s*×\s*(?:(\d+)\s*(?:reps|répétitions)|(\d+)\s*min)/);
            if (match) {
                seriesInput.value = match[1];
                if (match[2]) { // répétitions
                    repsInput.value = match[2];
                    durationInput.value = '';
                } else if (match[3]) { // durée
                    durationInput.value = match[3];
                    repsInput.value = '';
                }
            }
        }
    }

    saveExercise(button) {
        const exerciseItem = button.closest('.exercise-item');
        const editForm = exerciseItem.querySelector('.exercise-edit-form');
        
        // Récupérer les nouvelles valeurs
        const exerciseSelect = editForm.querySelector('select[name="exercise-select"]');
        const newSeries = editForm.querySelector('input[name="series"]').value;
        const newReps = editForm.querySelector('input[name="repetitions"]').value;
        const newDuration = editForm.querySelector('input[name="duration"]').value;
        
        if (!exerciseSelect.value || !newSeries) {
            alert('Veuillez sélectionner un exercice et spécifier le nombre de séries');
            return;
        }
        
        const selectedExercise = this.exercisesList.find(ex => ex.id == exerciseSelect.value);
        const measurementType = selectedExercise.measurement_type;
        
        if (measurementType === 'time' && !newDuration) {
            alert('Veuillez spécifier la durée pour cet exercice');
            return;
        } else if (measurementType === 'repetitions' && !newReps) {
            alert('Veuillez spécifier le nombre de répétitions pour cet exercice');
            return;
        }
        
        // Mettre à jour l'affichage
        exerciseItem.querySelector('h5').textContent = selectedExercise.name;
        
        let typeText = `${newSeries} séries × `;
        if (measurementType === 'time') {
            typeText += `${newDuration} min`;
        } else {
            typeText += `${newReps} répétitions`;
        }
        exerciseItem.querySelector('.exercise-type').textContent = typeText;
        
        // Mettre à jour les données
        const exerciseData = {
            nom: selectedExercise.name,
            series: parseInt(newSeries)
        };
        
        if (measurementType === 'time') {
            exerciseData.duree_minutes = parseInt(newDuration);
        } else {
            exerciseData.repetitions = parseInt(newReps);
        }
        
        this.updateExerciseData(exerciseItem, exerciseData);
        
        // Fermer le formulaire d'édition
        this.cancelEdit(button);
        
        // Marquer comme modifié
        this.markAsModified();
    }

    cancelEdit(button) {
        const exerciseItem = button.closest('.exercise-item');
        const editForm = exerciseItem.querySelector('.exercise-edit-form');
        
        exerciseItem.classList.remove('editing');
        editForm.classList.remove('active');
    }

    deleteExercise(button) {
        if (confirm('Êtes-vous sûr de vouloir supprimer cet exercice ?')) {
            const exerciseItem = button.closest('.exercise-item');
            const dayCard = exerciseItem.closest('.day-card');
            
            // Supprimer l'exercice des données
            this.removeExerciseData(exerciseItem);
            
            exerciseItem.remove();
            this.markAsModified();
            
            // Si plus d'exercices, afficher un message
            const remainingExercises = dayCard.querySelectorAll('.exercise-item');
            if (remainingExercises.length === 0) {
                const exercisesList = dayCard.querySelector('.exercises-list');
                exercisesList.innerHTML = '<p>Aucun exercice. <button class="add-exercise-btn">Ajouter un exercice</button></p>';
            }
        }
    }

    addExercise(button) {
        const dayCard = button.closest('.day-card');
        const addForm = dayCard.querySelector('.add-exercise-form');
        
        if (addForm) {
            addForm.style.display = 'block';
            button.style.display = 'none';
            
            // Réinitialiser le formulaire
            addForm.reset();
            
            // S'assurer que les selects sont peuplés
            this.populateExerciseSelects();
        }
    }

    createExerciseHTML(exercise) {
        const typeText = exercise.repetitions 
            ? `${exercise.series} séries × ${exercise.repetitions} répétitions`
            : `${exercise.series} séries × ${exercise.duree_minutes} min`;
            
        return `
            <div class="exercise-item">
                <div class="exercise-header">
                    <h5>${exercise.nom}</h5>
                    <span class="exercise-type">${typeText}</span>
                </div>
                <div class="exercise-actions">
                    <button class="btn-edit">Modifier</button>
                    <button class="btn-delete">Supprimer</button>
                </div>
                <div class="exercise-edit-form">
                    <div class="edit-form-grid">
                        <div class="edit-form-group">
                            <label>Exercice</label>
                            <select name="exercise-select" required>
                                <option value="">Choisir un exercice...</option>
                            </select>
                        </div>
                        <div class="edit-form-group">
                            <label>Séries</label>
                            <input type="number" name="series" min="1" required>
                        </div>
                        <div class="edit-form-group exercise-repetitions-group">
                            <label>Répétitions</label>
                            <input type="number" name="repetitions" min="1">
                        </div>
                        <div class="edit-form-group exercise-duration-group" style="display: none;">
                            <label>Durée (minutes)</label>
                            <input type="number" name="duration" min="1">
                        </div>
                    </div>
                    <div class="edit-form-actions">
                        <button class="btn btn-success btn-small btn-save-exercise">Sauvegarder</button>
                        <button class="btn btn-cancel btn-small btn-cancel-edit">Annuler</button>
                    </div>
                </div>
            </div>
        `;
    }

    updateExerciseData(exerciseItem, newData) {
        // Trouver l'exercice dans les données et le mettre à jour
        const dayCard = exerciseItem.closest('.day-card');
        const dayIndex = Array.from(dayCard.parentNode.children).indexOf(dayCard);
        const exerciseIndex = Array.from(dayCard.querySelectorAll('.exercise-item')).indexOf(exerciseItem);
        
        if (this.workoutPlan && this.workoutPlan.jours[dayIndex] && this.workoutPlan.jours[dayIndex].exercices[exerciseIndex]) {
            this.workoutPlan.jours[dayIndex].exercices[exerciseIndex] = newData;
        }
    }

    addExerciseData(dayCard, exerciseData) {
        const dayIndex = Array.from(dayCard.parentNode.children).indexOf(dayCard);
        
        if (this.workoutPlan && this.workoutPlan.jours[dayIndex]) {
            if (!this.workoutPlan.jours[dayIndex].exercices) {
                this.workoutPlan.jours[dayIndex].exercices = [];
            }
            this.workoutPlan.jours[dayIndex].exercices.push(exerciseData);
        }
    }

    removeExerciseData(exerciseItem) {
        const dayCard = exerciseItem.closest('.day-card');
        const dayIndex = Array.from(dayCard.parentNode.children).indexOf(dayCard);
        const exerciseIndex = Array.from(dayCard.querySelectorAll('.exercise-item')).indexOf(exerciseItem);
        
        if (this.workoutPlan && this.workoutPlan.jours[dayIndex] && this.workoutPlan.jours[dayIndex].exercices) {
            this.workoutPlan.jours[dayIndex].exercices.splice(exerciseIndex, 1);
        }
    }

    renderEditablePlan() {
        const container = document.querySelector('.workout-plan-container');
        if (!container || !this.workoutPlan) return;
        
        // Ajouter les boutons d'édition aux exercices existants
        container.querySelectorAll('.exercise-item').forEach(item => {
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
        container.querySelectorAll('.day-card.workout-day').forEach(dayCard => {
            if (!dayCard.querySelector('.add-exercise-btn')) {
                const exercisesList = dayCard.querySelector('.exercises-list');
                if (exercisesList) {
                    exercisesList.insertAdjacentHTML('afterend', '<button class="add-exercise-btn">+ Ajouter un exercice</button>');
                }
            }
        });
    }

    markAsModified() {
        this.isModified = true;
        
        // Afficher un indicateur de modification
        if (!document.querySelector('.plan-modified')) {
            const container = document.querySelector('.workout-plan-container');
            const modifiedIndicator = document.createElement('div');
            modifiedIndicator.classList.add('plan-modified');
            modifiedIndicator.innerHTML = '<p>✏️ Programme modifié - Les changements seront sauvegardés automatiquement</p>';
            container.parentNode.insertBefore(modifiedIndicator, container);
        }
        
        // Déclencher l'événement de sauvegarde
        document.dispatchEvent(new CustomEvent('plan-modified'));
    }

    async savePlan() {
        if (!this.isModified || !this.workoutPlan) return;
        
        try {
            const response = await fetch('/save-plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    plan: this.workoutPlan
                })
            });
            
            if (response.ok) {
                console.log('Plan sauvegardé avec succès');
                this.isModified = false;
                
                // Mettre à jour l'indicateur
                const modifiedIndicator = document.querySelector('.plan-modified p');
                if (modifiedIndicator) {
                    modifiedIndicator.innerHTML = '✅ Programme sauvegardé';
                    setTimeout(() => {
                        const indicator = document.querySelector('.plan-modified');
                        if (indicator) indicator.remove();
                    }, 2000);
                }
            }
        } catch (error) {
            console.error('Erreur lors de la sauvegarde:', error);
        }
    }

    async loadExercisesList() {
        try {
            const response = await fetch('/static/data/exercises.json');
            const exercises = await response.json();
            this.exercisesList = exercises;
            this.populateExerciseSelects();
        } catch (error) {
            console.error('Erreur lors du chargement des exercices:', error);
        }
    }

    populateExerciseSelects() {
        const selects = document.querySelectorAll('select[name="exercise-select"], select[name="new-exercise-select"]');
        selects.forEach(select => {
            // Vider le select sauf la première option
            while (select.children.length > 1) {
                select.removeChild(select.lastChild);
            }
            
            // Ajouter les exercices
            this.exercisesList.forEach(exercise => {
                const option = document.createElement('option');
                option.value = exercise.id;
                option.textContent = exercise.name;
                option.dataset.measurementType = exercise.measurement_type;
                select.appendChild(option);
            });
        });
    }

    handleExerciseSelection(select) {
        const selectedOption = select.options[select.selectedIndex];
        const measurementType = selectedOption.dataset.measurementType;
        const form = select.closest('.edit-form-grid, .add-exercise-form');
        
        if (form) {
            const repetitionsGroup = form.querySelector('.exercise-repetitions-group, .new-exercise-repetitions-group');
            const durationGroup = form.querySelector('.exercise-duration-group, .new-exercise-duration-group');
            
            if (measurementType === 'time') {
                // Exercice basé sur le temps
                if (repetitionsGroup) repetitionsGroup.style.display = 'none';
                if (durationGroup) durationGroup.style.display = 'block';
            } else {
                // Exercice basé sur les répétitions
                if (repetitionsGroup) repetitionsGroup.style.display = 'block';
                if (durationGroup) durationGroup.style.display = 'none';
            }
        }
    }

    saveNewExercise(button) {
        const form = button.closest('.add-exercise-form');
        const dayCard = form.closest('.day-card');
        
        const exerciseSelect = form.querySelector('select[name="new-exercise-select"]');
        const seriesInput = form.querySelector('input[name="new-series"]');
        const repetitionsInput = form.querySelector('input[name="new-repetitions"]');
        const durationInput = form.querySelector('input[name="new-duration"]');
        
        if (!exerciseSelect.value || !seriesInput.value) {
            alert('Veuillez remplir tous les champs obligatoires');
            return;
        }
        
        const selectedExercise = this.exercisesList.find(ex => ex.id == exerciseSelect.value);
        const measurementType = selectedExercise.measurement_type;
        
        let exerciseData;
        if (measurementType === 'time') {
            if (!durationInput.value) {
                alert('Veuillez saisir la durée');
                return;
            }
            exerciseData = {
                nom: selectedExercise.name,
                series: parseInt(seriesInput.value),
                duree_minutes: parseInt(durationInput.value)
            };
        } else {
            if (!repetitionsInput.value) {
                alert('Veuillez saisir le nombre de répétitions');
                return;
            }
            exerciseData = {
                nom: selectedExercise.name,
                series: parseInt(seriesInput.value),
                repetitions: parseInt(repetitionsInput.value)
            };
        }
        
        // Ajouter l'exercice au plan
        this.addExerciseData(dayCard, exerciseData);
        
        // Créer l'élément HTML
        const exercisesList = dayCard.querySelector('.exercises-list');
        const exerciseHTML = this.createExerciseHTML(exerciseData);
        exercisesList.insertAdjacentHTML('beforeend', exerciseHTML);
        
        // Masquer le formulaire
        form.style.display = 'none';
        
        // Réafficher le bouton d'ajout
        const addButton = dayCard.querySelector('.add-exercise-btn');
        addButton.style.display = 'block';
        
        // Réinitialiser le formulaire
        form.reset();
        
        // Marquer comme modifié
        this.markAsModified();
    }

    cancelAdd(button) {
        const form = button.closest('.add-exercise-form');
        const dayCard = form.closest('.day-card');
        const addButton = dayCard.querySelector('.add-exercise-btn');
        
        form.style.display = 'none';
        form.reset();
        addButton.style.display = 'block';
    }
}

// Initialiser l'éditeur quand le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.workout-plan-container')) {
        window.workoutEditor = new WorkoutEditor();
    }
});