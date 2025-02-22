// Handle token refresh
let lastRefresh = new Date();
const REFRESH_INTERVAL = 25 * 60 * 1000; // Refresh 5 minutes before expiry (25 minutes)

// Add HTMX headers and handle token refresh
document.body.addEventListener('htmx:configRequest', function(evt) {
    evt.detail.headers['Authorization'] = `Bearer ${accessToken}`;

    // Check if we need to refresh the token
    const now = new Date();
    if (now - lastRefresh > REFRESH_INTERVAL) {
        fetch(refreshTokenUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                refresh: refreshToken
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.access) {
                // Update the session storage
                fetch(updateTokenUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        access: data.access
                    })
                });
                lastRefresh = new Date();
            } else {
                // Token refresh failed, redirect to login
                window.location.href = loginUrl;
            }
        })
        .catch(() => {
            // On error, redirect to login
            window.location.href = loginUrl;
        });
    }
});

// Add loading class to the row being updated
document.body.addEventListener('htmx:beforeRequest', function(evt) {
    var target = evt.detail.target;
    if (target.tagName === 'TR') {
        target.classList.add('opacity-50');
    }
});

// Remove loading class after request completes
document.body.addEventListener('htmx:afterRequest', function(evt) {
    var target = evt.detail.target;
    if (target.tagName === 'TR') {
        target.classList.remove('opacity-50');
    }
});

// Handle unauthorized responses
document.body.addEventListener('htmx:responseError', function(evt) {
    if (evt.detail.xhr.status === 401) {
        window.location.href = loginUrl;
    }
}); 