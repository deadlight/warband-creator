document.addEventListener('DOMContentLoaded', function () {
    var overlay = document.getElementById('modal-overlay');
    var itemNameEl = document.getElementById('modal-item-name');
    var messageEl = document.getElementById('modal-message');
    var confirmBtn = document.getElementById('modal-confirm');
    var deleteForm = document.getElementById('modal-delete-form');
    var cancelBtn = document.getElementById('modal-cancel');

    function showModal(name, url, message, buttonLabel) {
        itemNameEl.textContent = name;
        messageEl.textContent = message || 'This cannot be undone.';
        confirmBtn.textContent = buttonLabel || 'Delete';
        deleteForm.action = url;
        overlay.classList.add('active');
    }

    function hideModal() {
        overlay.classList.remove('active');
        deleteForm.action = '';
    }

    cancelBtn.addEventListener('click', hideModal);

    overlay.addEventListener('click', function (e) {
        if (e.target === overlay) {
            hideModal();
        }
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && overlay.classList.contains('active')) {
            hideModal();
        }
    });

    document.addEventListener('click', function (e) {
        var trigger = e.target.closest('.js-delete-confirm');
        if (!trigger) return;
        e.preventDefault();

        var name = trigger.getAttribute('data-item-name') || 'this item';
        var url = trigger.getAttribute('data-delete-url');
        if (!url) return;

        var message = trigger.getAttribute('data-message');
        var buttonLabel = trigger.getAttribute('data-button-label');

        showModal(name, url, message, buttonLabel);
    });

    deleteForm.addEventListener('submit', function () {
        overlay.classList.remove('active');
    });
});
