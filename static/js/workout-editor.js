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
            }
        });

        // Sauvegarder automatiquement quand le plan est modifié
        document.addEventListener('plan-modified', () => {
            this.savePlan();
        });
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
            const nameInput = editForm.querySelector('input[name="exercise-name"]');
            const seriesInput = editForm.querySelector('input[name="series"]');
            const repsInput = editForm.querySelector('input[name="repetitions"]');
            const durationInput = editForm.querySelector('input[name="duration"]');
            
            nameInput.value = exerciseName;
            
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
        const newName = editForm.querySelector('input[name="exercise-name"]').value;
        const newSeries = editForm.querySelector('input[name="series"]').value;
        const newReps = editForm.querySelector('input[name="repetitions"]').value;
        const newDuration = editForm.querySelector('input[name="duration"]').value;
        
        if (!newName || !newSeries) {
            alert('Le nom et le nombre de séries sont obligatoires');
            return;
        }
        
        if (!newReps && !newDuration) {
            alert('Veuillez spécifier soit les répétitions soit la durée');
            return;
        }
        
        // Mettre à jour l'affichage
        exerciseItem.querySelector('h5').textContent = newName;
        
        let typeText = `${newSeries} séries × `;
        if (newReps) {
            typeText += `${newReps} répétitions`;
        } else {
            typeText += `${newDuration} min`;
        }
        exerciseItem.querySelector('.exercise-type').textContent = typeText;
        
        // Mettre à jour les données
        this.updateExerciseData(exerciseItem, {
            nom: newName,
            series: parseInt(newSeries),
            repetitions: newReps ? parseInt(newReps) : null,
            duree_minutes: newDuration ? parseInt(newDuration) : null
        });
        
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
        const exercisesList = dayCard.querySelector('.exercises-list');
        
        const newExerciseHTML = this.createExerciseHTML({
            nom: 'Nouvel exercice',
            series: 3,
            repetitions: 10,
            duree_minutes: null
        });
        
        // Si la liste est vide, la recréer
        if (!exercisesList || exercisesList.innerHTML.includes('Aucun exercice')) {
            const newList = document.createElement('div');
            newList.classList.add('exercises-list');
            newList.innerHTML = newExerciseHTML;
            
            if (exercisesList) {
                exercisesList.replaceWith(newList);
            } else {
                // Ajouter après le titre du jour
                const dayTitle = dayCard.querySelector('h4');
                dayTitle.insertAdjacentHTML('afterend', '<div class="exercises-list">' + newExerciseHTML + '</div>');
            }
        } else {
            exercisesList.insertAdjacentHTML('beforeend', newExerciseHTML);
        }
        
        // Ajouter aux données
        this.addExerciseData(dayCard, {
            nom: 'Nouvel exercice',
            series: 3,
            repetitions: 10,
            duree_minutes: null
        });
        
        this.markAsModified();
        
        // Ouvrir directement en édition
        setTimeout(() => {
            const newExercise = dayCard.querySelector('.exercise-item:last-child');
            const editButton = newExercise.querySelector('.btn-edit');
            this.editExercise(editButton);
        }, 100);
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
}

// Initialiser l'éditeur quand le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.workout-plan-container')) {
        window.workoutEditor = new WorkoutEditor();
    }
});