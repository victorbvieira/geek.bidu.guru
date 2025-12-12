/**
 * Admin Panel JavaScript - geek.bidu.guru
 */

// =============================================================================
// Sidebar Toggle (Mobile)
// =============================================================================

function toggleSidebar() {
    const sidebar = document.querySelector('.admin-sidebar');
    if (sidebar) {
        sidebar.classList.toggle('open');
    }
}

// Close sidebar when clicking outside on mobile
document.addEventListener('click', function(e) {
    const sidebar = document.querySelector('.admin-sidebar');
    const toggleBtn = document.querySelector('.sidebar-toggle');

    if (sidebar && sidebar.classList.contains('open')) {
        if (!sidebar.contains(e.target) && !toggleBtn?.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    }
});

// =============================================================================
// Form Utilities
// =============================================================================

/**
 * Mostra mensagem de feedback
 */
function showMessage(message, type = 'success') {
    const container = document.getElementById('message-container') || createMessageContainer();

    const alert = document.createElement('div');
    alert.className = `admin-alert admin-alert-${type}`;
    alert.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" class="admin-alert-close">&times;</button>
    `;

    container.appendChild(alert);

    // Auto-remove after 5 seconds
    setTimeout(() => alert.remove(), 5000);
}

function createMessageContainer() {
    const container = document.createElement('div');
    container.id = 'message-container';
    container.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 1000; display: flex; flex-direction: column; gap: 10px;';
    document.body.appendChild(container);
    return container;
}

/**
 * Confirma acao destrutiva
 */
function confirmAction(message) {
    return confirm(message || 'Tem certeza que deseja continuar?');
}

/**
 * Submit form com AJAX
 */
async function submitForm(form, options = {}) {
    const formData = new FormData(form);
    const method = form.method || 'POST';
    const url = form.action || window.location.href;

    try {
        const response = await fetch(url, {
            method: method,
            body: formData,
            headers: {
                'Accept': 'application/json',
            },
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(data.message || 'Operacao realizada com sucesso!', 'success');
            if (options.onSuccess) options.onSuccess(data);
        } else {
            showMessage(data.detail || 'Erro ao processar requisicao', 'danger');
            if (options.onError) options.onError(data);
        }

        return data;
    } catch (error) {
        showMessage('Erro de conexao', 'danger');
        console.error('Form submit error:', error);
        throw error;
    }
}

// =============================================================================
// Table Utilities
// =============================================================================

/**
 * Seleciona/deseleciona todos os checkboxes da tabela
 */
function toggleAllCheckboxes(source) {
    const checkboxes = document.querySelectorAll('.row-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = source.checked;
    });
    updateBulkActions();
}

/**
 * Atualiza visibilidade dos botoes de acao em massa
 */
function updateBulkActions() {
    const checked = document.querySelectorAll('.row-checkbox:checked');
    const bulkActions = document.querySelector('.bulk-actions');

    if (bulkActions) {
        bulkActions.style.display = checked.length > 0 ? 'flex' : 'none';
        const count = bulkActions.querySelector('.selected-count');
        if (count) count.textContent = checked.length;
    }
}

// Add event listeners to row checkboxes
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.row-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', updateBulkActions);
    });
});

// =============================================================================
// Delete Confirmation
// =============================================================================

/**
 * Confirma e executa delete
 */
async function deleteItem(url, itemName) {
    if (!confirmAction(`Tem certeza que deseja excluir "${itemName}"? Esta acao nao pode ser desfeita.`)) {
        return;
    }

    try {
        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'Accept': 'application/json',
            },
        });

        if (response.ok) {
            showMessage('Item excluido com sucesso!', 'success');
            // Reload page after short delay
            setTimeout(() => window.location.reload(), 1000);
        } else {
            const data = await response.json();
            showMessage(data.detail || 'Erro ao excluir item', 'danger');
        }
    } catch (error) {
        showMessage('Erro de conexao', 'danger');
        console.error('Delete error:', error);
    }
}

// =============================================================================
// Slug Generator
// =============================================================================

/**
 * Gera slug a partir do titulo
 */
function generateSlug(text) {
    return text
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '') // Remove acentos
        .replace(/[^a-z0-9\s-]/g, '') // Remove caracteres especiais
        .replace(/\s+/g, '-') // Espacos para hifens
        .replace(/-+/g, '-') // Remove hifens duplicados
        .replace(/^-|-$/g, ''); // Remove hifens no inicio/fim
}

/**
 * Auto-gera slug quando titulo muda
 */
function setupSlugGenerator(titleInput, slugInput) {
    if (!titleInput || !slugInput) return;

    titleInput.addEventListener('input', function() {
        // So gera automaticamente se o slug estiver vazio ou for igual ao titulo anterior
        if (!slugInput.dataset.manual) {
            slugInput.value = generateSlug(this.value);
        }
    });

    // Marca como manual se usuario editar diretamente
    slugInput.addEventListener('input', function() {
        this.dataset.manual = 'true';
    });
}

// =============================================================================
// Character Counter
// =============================================================================

/**
 * Adiciona contador de caracteres
 */
function setupCharCounter(input, maxLength) {
    const counter = document.createElement('span');
    counter.className = 'char-counter';
    counter.style.cssText = 'font-size: 0.75rem; color: var(--admin-text-muted); float: right;';

    const updateCounter = () => {
        const remaining = maxLength - input.value.length;
        counter.textContent = `${input.value.length}/${maxLength}`;
        counter.style.color = remaining < 20 ? 'var(--admin-danger)' : 'var(--admin-text-muted)';
    };

    input.parentNode.appendChild(counter);
    input.addEventListener('input', updateCounter);
    updateCounter();
}

// =============================================================================
// Init
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Setup slug generators
    const titleInput = document.getElementById('title');
    const slugInput = document.getElementById('slug');
    if (titleInput && slugInput) {
        setupSlugGenerator(titleInput, slugInput);
    }

    // Setup character counters for SEO fields
    const seoTitle = document.getElementById('seo_title');
    const seoDesc = document.getElementById('seo_description');
    if (seoTitle) setupCharCounter(seoTitle, 60);
    if (seoDesc) setupCharCounter(seoDesc, 160);
});
