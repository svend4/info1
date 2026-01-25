// Конфигурация API
const API_BASE_URL = 'http://localhost:5000/api';

// Состояние приложения
const state = {
    cards: [],
    currentView: 'all',
    currentFilters: {
        search: '',
        status: '',
        priority: '',
    },
    editingCard: null,
};

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    loadCards();
});

// Инициализация обработчиков событий
function initEventListeners() {
    // Навигация по типам карточек
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const view = e.target.dataset.view;
            if (view) {
                setActiveView(view);
            }
        });
    });

    // Создание карточки
    document.getElementById('btnCreateCard').addEventListener('click', () => {
        openCardModal();
    });

    // Закрытие модального окна
    document.getElementById('btnCloseModal').addEventListener('click', closeCardModal);
    document.getElementById('btnCancel').addEventListener('click', closeCardModal);

    // Клик вне модального окна
    document.getElementById('cardModal').addEventListener('click', (e) => {
        if (e.target.id === 'cardModal') {
            closeCardModal();
        }
    });

    // Отправка формы
    document.getElementById('cardForm').addEventListener('submit', (e) => {
        e.preventDefault();
        saveCard();
    });

    // Изменение типа карточки
    document.getElementById('cardType').addEventListener('change', (e) => {
        renderDynamicFields(e.target.value);
    });

    // Поиск
    document.getElementById('searchInput').addEventListener('input', (e) => {
        state.currentFilters.search = e.target.value;
        filterCards();
    });

    // Фильтры
    document.getElementById('filterStatus').addEventListener('change', (e) => {
        state.currentFilters.status = e.target.value;
        filterCards();
    });

    document.getElementById('filterPriority').addEventListener('change', (e) => {
        state.currentFilters.priority = e.target.value;
        filterCards();
    });

    // Обновление
    document.getElementById('btnRefresh').addEventListener('click', () => {
        loadCards();
    });
}

// Установка активного вида
function setActiveView(view) {
    state.currentView = view;

    // Обновить активную кнопку
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.view === view) {
            btn.classList.add('active');
        }
    });

    renderCards();
}

// Загрузка карточек с сервера
async function loadCards() {
    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/cards`);

        if (!response.ok) {
            throw new Error('Ошибка загрузки карточек');
        }

        const data = await response.json();
        state.cards = data.cards || [];

        updateStats();
        renderCards();
    } catch (error) {
        console.error('Ошибка:', error);
        showError('Не удалось загрузить карточки. Убедитесь, что API сервер запущен.');
    }
}

// Отображение загрузки
function showLoading() {
    const container = document.getElementById('cardsContainer');
    container.innerHTML = '<div class="loading">Загрузка карточек...</div>';
}

// Отображение ошибки
function showError(message) {
    const container = document.getElementById('cardsContainer');
    container.innerHTML = `
        <div class="empty-state">
            <h2>⚠️ Ошибка</h2>
            <p>${message}</p>
            <button onclick="loadCards()" class="btn-refresh" style="margin-top: 20px;">
                Попробовать снова
            </button>
        </div>
    `;
}

// Обновление статистики
function updateStats() {
    const total = state.cards.length;
    const active = state.cards.filter(c => c.status === 'active').length;
    const completed = state.cards.filter(c => c.status === 'completed').length;

    // Просроченные (имеют deadline в прошлом и не завершены)
    const now = new Date();
    const overdue = state.cards.filter(c => {
        if (c.status === 'completed' || !c.deadline) return false;
        const deadline = new Date(c.deadline);
        return deadline < now;
    }).length;

    document.getElementById('statTotal').textContent = total;
    document.getElementById('statActive').textContent = active;
    document.getElementById('statCompleted').textContent = completed;
    document.getElementById('statOverdue').textContent = overdue;
}

// Рендеринг карточек
function renderCards() {
    const container = document.getElementById('cardsContainer');
    let filteredCards = getFilteredCards();

    if (filteredCards.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h2>📭 Нет карточек</h2>
                <p>Создайте свою первую карточку!</p>
            </div>
        `;
        return;
    }

    container.innerHTML = filteredCards.map(card => createCardHTML(card)).join('');

    // Добавить обработчики для кнопок карточек
    container.querySelectorAll('.btn-edit').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const cardId = e.target.closest('.card').dataset.id;
            editCard(cardId);
        });
    });

    container.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const cardId = e.target.closest('.card').dataset.id;
            deleteCard(cardId);
        });
    });
}

// Получение отфильтрованных карточек
function getFilteredCards() {
    let filtered = state.cards;

    // Фильтр по типу (вид)
    if (state.currentView !== 'all') {
        filtered = filtered.filter(card => card.type === state.currentView);
    }

    // Фильтр по поиску
    if (state.currentFilters.search) {
        const query = state.currentFilters.search.toLowerCase();
        filtered = filtered.filter(card =>
            card.title.toLowerCase().includes(query) ||
            (card.description && card.description.toLowerCase().includes(query))
        );
    }

    // Фильтр по статусу
    if (state.currentFilters.status) {
        filtered = filtered.filter(card => card.status === state.currentFilters.status);
    }

    // Фильтр по приоритету
    if (state.currentFilters.priority) {
        filtered = filtered.filter(card => card.priority === state.currentFilters.priority);
    }

    return filtered;
}

// Фильтрация карточек
function filterCards() {
    renderCards();
}

// Создание HTML карточки
function createCardHTML(card) {
    const typeIcons = {
        task: '✓',
        medicine: '💊',
        contact: '👤',
        appointment: '📅',
        shopping: '🛒',
        note: '📝',
        project: '📁',
    };

    const typeLabels = {
        task: 'Задача',
        medicine: 'Лекарство',
        contact: 'Контакт',
        appointment: 'Встреча',
        shopping: 'Покупка',
        note: 'Заметка',
        project: 'Проект',
    };

    const details = getCardDetails(card);

    return `
        <div class="card priority-${card.priority || 'medium'}" data-id="${card.id}">
            <div class="card-header">
                <span class="card-type">${typeIcons[card.type]}</span>
                <div class="card-actions">
                    <button class="btn-icon btn-edit" title="Редактировать">✏️</button>
                    <button class="btn-icon btn-delete delete" title="Удалить">🗑️</button>
                </div>
            </div>
            <h3 class="card-title">${escapeHtml(card.title)}</h3>
            ${card.description ? `<p class="card-description">${escapeHtml(card.description)}</p>` : ''}
            <div class="card-meta">
                <span class="badge status-${card.status}">${getStatusLabel(card.status)}</span>
                <span class="badge">${typeLabels[card.type]}</span>
            </div>
            ${details ? `<div class="card-details">${details}</div>` : ''}
            ${card.tags && card.tags.length > 0 ? `
                <div class="card-tags">
                    ${card.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                </div>
            ` : ''}
        </div>
    `;
}

// Получение деталей карточки
function getCardDetails(card) {
    const details = [];

    if (card.deadline) {
        const deadline = new Date(card.deadline);
        details.push(`<div class="card-details-item"><strong>Срок:</strong> ${formatDate(deadline)}</div>`);
    }

    if (card.type === 'medicine' && card.dosage) {
        details.push(`<div class="card-details-item"><strong>Дозировка:</strong> ${escapeHtml(card.dosage)}</div>`);
    }

    if (card.type === 'medicine' && card.schedule) {
        details.push(`<div class="card-details-item"><strong>График:</strong> ${card.schedule.join(', ')}</div>`);
    }

    if (card.type === 'contact' && card.phone) {
        details.push(`<div class="card-details-item"><strong>Телефон:</strong> ${escapeHtml(card.phone)}</div>`);
    }

    if (card.type === 'appointment' && card.location) {
        details.push(`<div class="card-details-item"><strong>Место:</strong> ${escapeHtml(card.location)}</div>`);
    }

    if (card.type === 'shopping' && card.quantity) {
        details.push(`<div class="card-details-item"><strong>Количество:</strong> ${card.quantity}</div>`);
    }

    return details.join('');
}

// Метка статуса
function getStatusLabel(status) {
    const labels = {
        pending: 'Ожидает',
        active: 'Активно',
        completed: 'Завершено',
        cancelled: 'Отменено',
    };
    return labels[status] || status;
}

// Форматирование даты
function formatDate(date) {
    return new Intl.DateTimeFormat('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    }).format(date);
}

// Экранирование HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Открытие модального окна
function openCardModal(card = null) {
    state.editingCard = card;

    const modal = document.getElementById('cardModal');
    const form = document.getElementById('cardForm');
    const title = document.getElementById('modalTitle');

    // Сброс формы
    form.reset();
    document.getElementById('dynamicFields').innerHTML = '';

    if (card) {
        // Режим редактирования
        title.textContent = 'Редактировать карточку';
        fillFormWithCard(card);
    } else {
        // Режим создания
        title.textContent = 'Создать карточку';
    }

    modal.classList.add('active');
}

// Закрытие модального окна
function closeCardModal() {
    const modal = document.getElementById('cardModal');
    modal.classList.remove('active');
    state.editingCard = null;
}

// Заполнение формы данными карточки
function fillFormWithCard(card) {
    document.getElementById('cardType').value = card.type;
    document.getElementById('cardTitle').value = card.title;
    document.getElementById('cardDescription').value = card.description || '';
    document.getElementById('cardStatus').value = card.status;
    document.getElementById('cardPriority').value = card.priority || 'medium';
    document.getElementById('cardTags').value = card.tags ? card.tags.join(', ') : '';

    renderDynamicFields(card.type, card);
}

// Рендеринг динамических полей
function renderDynamicFields(type, card = null) {
    const container = document.getElementById('dynamicFields');
    container.innerHTML = '';

    if (type === 'task' || type === 'appointment' || type === 'project') {
        container.innerHTML += `
            <div class="form-group">
                <label for="cardDeadline">Срок выполнения</label>
                <input type="datetime-local" id="cardDeadline" value="${card?.deadline || ''}">
            </div>
        `;
    }

    if (type === 'medicine') {
        container.innerHTML += `
            <div class="form-group">
                <label for="cardDosage">Дозировка</label>
                <input type="text" id="cardDosage" placeholder="10 мг" value="${card?.dosage || ''}">
            </div>
            <div class="form-group">
                <label for="cardSchedule">График приема (через запятую)</label>
                <input type="text" id="cardSchedule" placeholder="09:00, 21:00" value="${card?.schedule?.join(', ') || ''}">
            </div>
        `;
    }

    if (type === 'contact') {
        container.innerHTML += `
            <div class="form-group">
                <label for="cardPhone">Телефон</label>
                <input type="tel" id="cardPhone" placeholder="+7 (999) 123-45-67" value="${card?.phone || ''}">
            </div>
            <div class="form-group">
                <label for="cardEmail">Email</label>
                <input type="email" id="cardEmail" placeholder="example@mail.com" value="${card?.email || ''}">
            </div>
        `;
    }

    if (type === 'appointment') {
        container.innerHTML += `
            <div class="form-group">
                <label for="cardLocation">Место встречи</label>
                <input type="text" id="cardLocation" placeholder="ул. Ленина, д. 10" value="${card?.location || ''}">
            </div>
        `;
    }

    if (type === 'shopping') {
        container.innerHTML += `
            <div class="form-row">
                <div class="form-group">
                    <label for="cardQuantity">Количество</label>
                    <input type="number" id="cardQuantity" value="${card?.quantity || 1}">
                </div>
                <div class="form-group">
                    <label for="cardPrice">Цена</label>
                    <input type="number" id="cardPrice" step="0.01" placeholder="0.00" value="${card?.price || ''}">
                </div>
            </div>
        `;
    }
}

// Сохранение карточки
async function saveCard() {
    const type = document.getElementById('cardType').value;
    const title = document.getElementById('cardTitle').value;
    const description = document.getElementById('cardDescription').value;
    const status = document.getElementById('cardStatus').value;
    const priority = document.getElementById('cardPriority').value;
    const tagsInput = document.getElementById('cardTags').value;

    const cardData = {
        type,
        title,
        description,
        status,
        priority,
        tags: tagsInput ? tagsInput.split(',').map(t => t.trim()).filter(t => t) : [],
    };

    // Добавить специфичные поля
    const deadlineEl = document.getElementById('cardDeadline');
    if (deadlineEl && deadlineEl.value) {
        cardData.deadline = new Date(deadlineEl.value).toISOString();
    }

    if (type === 'medicine') {
        const dosageEl = document.getElementById('cardDosage');
        const scheduleEl = document.getElementById('cardSchedule');
        if (dosageEl) cardData.dosage = dosageEl.value;
        if (scheduleEl && scheduleEl.value) {
            cardData.schedule = scheduleEl.value.split(',').map(t => t.trim()).filter(t => t);
        }
    }

    if (type === 'contact') {
        const phoneEl = document.getElementById('cardPhone');
        const emailEl = document.getElementById('cardEmail');
        if (phoneEl) cardData.phone = phoneEl.value;
        if (emailEl) cardData.email = emailEl.value;
    }

    if (type === 'appointment') {
        const locationEl = document.getElementById('cardLocation');
        if (locationEl) cardData.location = locationEl.value;
    }

    if (type === 'shopping') {
        const quantityEl = document.getElementById('cardQuantity');
        const priceEl = document.getElementById('cardPrice');
        if (quantityEl) cardData.quantity = parseInt(quantityEl.value) || 1;
        if (priceEl && priceEl.value) cardData.price = parseFloat(priceEl.value);
    }

    try {
        let response;
        if (state.editingCard) {
            // Обновление существующей карточки
            response = await fetch(`${API_BASE_URL}/cards/${state.editingCard.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(cardData),
            });
        } else {
            // Создание новой карточки
            response = await fetch(`${API_BASE_URL}/cards`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(cardData),
            });
        }

        if (!response.ok) {
            throw new Error('Ошибка сохранения карточки');
        }

        closeCardModal();
        loadCards();
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Не удалось сохранить карточку. Проверьте подключение к серверу.');
    }
}

// Редактирование карточки
function editCard(cardId) {
    const card = state.cards.find(c => c.id === cardId);
    if (card) {
        openCardModal(card);
    }
}

// Удаление карточки
async function deleteCard(cardId) {
    if (!confirm('Вы уверены, что хотите удалить эту карточку?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/cards/${cardId}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            throw new Error('Ошибка удаления карточки');
        }

        loadCards();
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Не удалось удалить карточку. Проверьте подключение к серверу.');
    }
}
