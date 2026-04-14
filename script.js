// Initialize Lucide Icons on load
document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
});

function revealDomains() {
    const inputField = document.getElementById('domainSearch');
    const input = inputField.value.trim().toLowerCase();
    const results = document.getElementById('resultsArea');
    
    if (!input) {
        results.style.display = 'none';
        return;
    }

    // Cleaning the input to be domain-friendly
    const base = input.split('.')[0].replace(/[^a-z0-9]/g, '');
    
    const data = [
        { ext: '.finance', price: '$19', status: 'Available' },
        { ext: '.com', price: '$12', status: 'Premium' },
        { ext: '.app', price: '$15', status: 'Available' },
        { ext: '.io', price: '$49', status: 'Limited' }
    ];

    results.innerHTML = '';
    results.style.display = 'block';

    data.forEach((item, index) => {
        const row = document.createElement('div');
        row.className = 'row fade-in';
        row.style.animationDelay = `${index * 0.1}s`;
        
        row.innerHTML = `
            <div>
                <span style="font-weight:600; font-size: 1.1rem;">${base}${item.ext}</span>
                <div style="color:var(--neon-green); font-size:0.75rem; margin-top:4px;">
                    <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--neon-green); margin-right:5px;"></span>
                    ${item.status}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-weight:700; font-size: 1.1rem;">${item.price}</div>
                <div style="font-size: 0.7rem; color: var(--text-muted);">per year</div>
            </div>
        `;
        results.appendChild(row);
    });
}

// Add scroll-based reveal (Optional extra polish)
const observerOptions = { threshold: 0.1 };
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
        }
    });
}, observerOptions);

document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));