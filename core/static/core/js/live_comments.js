document.addEventListener('DOMContentLoaded', function() {
    const titleElement = document.querySelector('#post-title');
    if (!titleElement) return;

    const postSlug = titleElement.dataset.slug;
    const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${wsScheme}://${window.location.host}/ws/post/${postSlug}/`);

    ws.onopen = function() {
        console.log("✅ WebSocket connected");
    }

    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);

        // Пример обработки сообщения
        if (data.type === 'comment') {
            const container = document.querySelector('#comments-container');
            if (container) container.innerHTML = data.html;
        }
    }

    ws.onclose = function() {
        console.log("❌ WebSocket disconnected");
    }

    // Отправка комментария
    const form = document.querySelector('#comment-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const content = form.querySelector('textarea').value;
            ws.send(JSON.stringify({
                'type': 'comment',
                'content': content
            }));
            form.reset();
        });
    }
});
