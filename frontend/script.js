const API_BASE_URL = 'http://localhost:8000/api/v1/admin';
const CLUB_ID = 1;

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById('datePicker').valueAsDate = new Date();
    loadData();
});

async function loadData() {
    const targetDate = document.getElementById('datePicker').value;

    // Показываем состояние загрузки
    document.getElementById('dialogsContainer').innerHTML = `
        <div class="empty-state">
            <i class="fas fa-circle-notch fa-spin"></i>
            <p>Анализируем диалоги...</p>
        </div>`;

    Promise.all([
        fetchSummary(targetDate),
        fetchDialogs(targetDate)
    ]);
}

async function fetchSummary(date) {
    try {
        const response = await fetch(`${API_BASE_URL}/summary?target_date=${date}&club_id=${CLUB_ID}`);
        if (!response.ok) throw new Error("Network response was not ok");
        const data = await response.json();

        if (data.message) {
            updateMetrics(0, "0%", 0);
        } else {
            updateMetrics(data.total_dialogs, `${data.negative_share_percent}%`, data.sales_count);
        }
    } catch (error) {
        console.error("Ошибка загрузки сводки:", error);
        updateMetrics("-", "-", "-");
    }
}

function updateMetrics(total, negative, sales) {
    document.getElementById('val-total').innerText = total;
    document.getElementById('val-negative').innerText = negative;
    document.getElementById('val-sales').innerText = sales;
}

async function fetchDialogs(date) {
    try {
        const response = await fetch(`${API_BASE_URL}/dialogs?date_filter=${date}&club_id=${CLUB_ID}`);
        if (!response.ok) throw new Error("Network response was not ok");
        const dialogs = await response.json();
        const container = document.getElementById('dialogsContainer');
        container.innerHTML = '';

        if (dialogs.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <p>За эту дату нет записей диалогов.</p>
                </div>`;
            return;
        }

        dialogs.forEach((dialog, index) => {
            const hasViolations = dialog.violations && dialog.violations.length > 0;
            const score = dialog.score || 0;

            // Определяем цвет и иконку тональности
            let toneClass = 'badge-tone-neu';
            let toneIcon = 'fa-meh';
            if (dialog.tonality === 'негатив') { toneClass = 'badge-tone-neg'; toneIcon = 'fa-frown'; }
            if (dialog.tonality === 'позитив') { toneClass = 'badge-tone-pos'; toneIcon = 'fa-smile'; }

            // Цвет прогресс-бара рейтинга
            let barColor = 'var(--success)';
            if (score < 50) barColor = 'var(--danger)';
            else if (score < 80) barColor = 'var(--warning)';

            // Сборка HTML нарушений
            let violationsHtml = '';
            if (hasViolations) {
                violationsHtml = dialog.violations.map(v => `
                    <div class="violation-quote">
                        <i class="fas fa-exclamation-triangle"></i>
                        <div>
                            <strong>Критическое нарушение: ${v.trigger_type}</strong>
                            «${v.quote}»
                        </div>
                    </div>
                `).join('');
            }

            // Инициалы сотрудника
            const empName = dialog.employee_name || 'Неизвестный';
            const initials = empName.substring(0, 2).toUpperCase();

            // Статус диалога (обводка)
            let cardClass = '';
            if (hasViolations) cardClass = 'violation';
            else if (score >= 90) cardClass = 'perfect';

            // Имитация небольшой задержки анимации для каждого элемента
            const animDelay = index * 0.1;

            const dialogHtml = `
                <div class="dialog-card ${cardClass}" style="animation-delay: ${animDelay}s">
                    <div class="dialog-header">
                        <div class="employee-info">
                            <div class="employee-avatar">${initials}</div>
                            ${empName}
                        </div>
                        <div class="score-box">
                            <div class="score-value">${score.toFixed(1)} / 100</div>
                            <div class="score-bar-bg">
                                <div class="score-bar-fill" style="width: ${score}%; background: ${barColor}"></div>
                            </div>
                        </div>
                    </div>
                    <div class="dialog-body">
                        <div class="badges">
                            <span class="badge badge-type"><i class="fas fa-tag"></i> ${dialog.dialog_type || 'прочее'}</span>
                            <span class="badge ${toneClass}"><i class="fas ${toneIcon}"></i> ${dialog.tonality || 'нейтрально'}</span>
                            ${hasViolations ? `<span class="badge badge-viol"><i class="fas fa-ban"></i> Найдено нарушение</span>` : ''}
                        </div>
                        
                        ${violationsHtml}
                        
                        <div class="completed-blocks">
                            <strong>Выполнены блоки:</strong> 
                            ${dialog.completed_blocks && dialog.completed_blocks.length > 0 
                                ? dialog.completed_blocks.map(b => `<span>Шаг #${b.block_id}</span>`).join('') 
                                : 'Нет данных'}
                        </div>
                    </div>
                </div>
            `;
            container.innerHTML += dialogHtml;
        });
    } catch (error) {
        console.error("Ошибка загрузки диалогов:", error);
        document.getElementById('dialogsContainer').innerHTML = `
            <div class="empty-state" style="color: var(--danger)">
                <i class="fas fa-wifi"></i>
                <p>Ошибка связи с сервером API. Убедитесь, что бэкенд запущен.</p>
            </div>`;
    }
}
window.onload = async () => {
    await fetchEmployees();
    setDate('today');
};

async function fetchEmployees() {
    try {
        const res = await fetch(`http://127.0.0.1:8000/api/v1/admin/employees?club_id=${clubId}`);
        const emps = await res.json();
        const select = document.getElementById('emp-select');
        emps.forEach(e => {
            select.innerHTML += `<option value="${e.id}">${e.name}</option>`;
        });
    } catch (e) { console.error("Ошибка загрузки сотрудников"); }
}

function loadData() {
    const selectedDate = document.getElementById('date-select').value;
    const empId = document.getElementById('emp-select').value;
    let extraParam = empId ? `&employee_id=${empId}` : '';

    fetchSummary(selectedDate, extraParam);
    fetchDialogs(selectedDate, extraParam);
}

async function fetchSummary(dateStr, extraParam) {
    try {
        const res = await fetch(`http://127.0.0.1:8000/api/v1/admin/summary?target_date=${dateStr}&club_id=${clubId}${extraParam}`);
        const data = await res.json();
        document.getElementById('val-total').innerText = data.total_dialogs || 0;
        const negVal = document.getElementById('val-negative');
        negVal.innerText = (data.negative_share_percent || 0) + '%';
        negVal.className = data.negative_share_percent > 0 ? 'card-value val-red' : 'card-value';
    } catch (e) { console.error(e); }
}

async function fetchDialogs(dateStr, extraParam) {
    try {
        const res = await fetch(`http://127.0.0.1:8000/api/v1/admin/dialogs?target_date=${dateStr}&club_id=${clubId}${extraParam}`);
        currentDialogs = await res.json();
        renderTable();
    } catch (e) { console.error(e); }
}