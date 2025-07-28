document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('infoForm');
    const resultSection = document.getElementById('resultSection');
    const programContainer = document.getElementById('programContainer');
    const productList = document.getElementById('productList');
    const exerciseListDiv = document.getElementById('exerciseList');

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
            const data = await response.json();
            // Essayer d'interpréter la réponse comme JSON structuré
            let schedule;
            try {
                schedule = JSON.parse(data.plan);
            } catch (e) {
                // Si ce n'est pas un JSON valide, afficher le texte brutf
                programContainer.textContent = data.plan;
                schedule = null;
            }
            if (schedule) {
                renderSchedule(schedule);
            }
            // Afficher les produits
            data.products.forEach(prod => {
                const li = document.createElement('li');
                const anchor = document.createElement('a');
                anchor.href = prod.link || '#';
                anchor.target = '_blank';
                anchor.rel = 'noopener noreferrer';
                anchor.textContent = prod.name;
                const span = document.createElement('span');
                span.textContent = ` – ${prod.description}`;
                li.appendChild(anchor);
                li.appendChild(span);
                productList.appendChild(li);
            });
        } catch (error) {
            programOutput.textContent = 'Une erreur est survenue lors de la génération du programme.';
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
            const title = document.createElement('h4');
            title.textContent = dayObj.nomJour || `Jour ${dayIndex + 1}`;
            card.appendChild(title);
            // Liste des exercices
            if (Array.isArray(dayObj.exercices)) {
                dayObj.exercices.forEach((exercise, exIndex) => {
                    const row = document.createElement('div');
                    row.classList.add('exercise-row');
                    // Sélecteur d'exercice
                    const select = document.createElement('select');
                    exerciseData.forEach(opt => {
                        const option = document.createElement('option');
                        option.value = opt.name;
                        option.textContent = opt.name;
                        if (opt.name.toLowerCase() === (exercise.nom || '').toLowerCase()) {
                            option.selected = true;
                        }
                        select.appendChild(option);
                    });
                    // Champ séries
                    const seriesLabel = document.createElement('label');
                    seriesLabel.textContent = 'Séries:';
                    const seriesInput = document.createElement('input');
                    seriesInput.type = 'number';
                    seriesInput.min = '1';
                    seriesInput.value = exercise.series || '';
                    seriesLabel.appendChild(seriesInput);
                    // Champ répétitions
                    const repsLabel = document.createElement('label');
                    repsLabel.textContent = ' Répétitions:';
                    const repsInput = document.createElement('input');
                    repsInput.type = 'number';
                    repsInput.min = '1';
                    repsInput.value = exercise.repetitions || '';
                    repsLabel.appendChild(repsInput);
                    // Champ durée
                    const durLabel = document.createElement('label');
                    durLabel.textContent = ' Durée (min):';
                    const durInput = document.createElement('input');
                    durInput.type = 'number';
                    durInput.min = '0';
                    durInput.value = exercise.duree_minutes || '';
                    durLabel.appendChild(durInput);
                    // Append all to row
                    row.appendChild(select);
                    row.appendChild(seriesLabel);
                    row.appendChild(repsLabel);
                    row.appendChild(durLabel);
                    card.appendChild(row);
                });
            }
            programContainer.appendChild(card);
        });
    }
});