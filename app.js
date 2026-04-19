document.addEventListener('DOMContentLoaded', () => {
    let allTools = [];
    const mainGrid = document.getElementById('mainGrid');
    const featuredGrid = document.getElementById('featuredGrid');
    const featuredSection = document.getElementById('featuredSection');
    const searchBar = document.getElementById('searchBar');
    const categoryFilters = document.getElementById('categoryFilters');

    // Cargar datos
    fetch('data/tools.json')
        .then(response => response.json())
        .then(data => {
            allTools = data;
            init();
        })
        .catch(err => {
            console.error("Error cargando herramientas:", err);
            // Datos de prueba para pre-render si el archivo no existe
            allTools = []; 
        });

    function init() {
        // Sort explicitly by id descending so newest are on top
        allTools.sort((a, b) => b.id - a.id);
        
        // Mark top 5 as featured/new
        for(let i = 0; i < Math.min(5, allTools.length); i++) {
            allTools[i].isNew = true;
        }

        renderCategories();
        renderTools(allTools);
    }

    function renderCategories() {
        const categories = ['all', ...new Set(allTools.map(t => t.categoria))];
        categoryFilters.innerHTML = '';
        categories.forEach(cat => {
            const chip = document.createElement('span');
            chip.className = `chip ${cat === 'all' ? 'active' : ''}`;
            chip.textContent = cat === 'all' ? 'Todos' : cat;
            chip.dataset.category = cat;
            chip.addEventListener('click', () => {
                document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                filterTools();
            });
            categoryFilters.appendChild(chip);
        });
    }

    function renderTools(tools) {
        mainGrid.innerHTML = '';
        tools.forEach(tool => {
            const card = createCard(tool);
            mainGrid.appendChild(card);
        });
    }

    function createCard(tool) {
        const linkWrapper = document.createElement('a');
        linkWrapper.href = tool.url;
        linkWrapper.target = "_blank";
        linkWrapper.className = 'card-link';

        const card = document.createElement('div');
        card.className = 'card';

        const newBadge = tool.isNew ? '<span class="badge-new">NUEVA</span>' : '';

        card.innerHTML = `
            <div class="card-title">
                <span>${tool.nombre} ${newBadge}</span>
                <span class="card-arrow">&rarr;</span>
            </div>
            <div class="card-desc">${tool.descripcion}</div>
            <div class="card-tags">
                ${tool.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
            </div>
        `;
        
        linkWrapper.appendChild(card);
        return linkWrapper;
    }

    function filterTools() {
        const searchTerm = searchBar.value.toLowerCase();
        const activeCategory = document.querySelector('.chip.active').dataset.category;

        const filtered = allTools.filter(tool => {
            const matchesSearch = tool.nombre.toLowerCase().includes(searchTerm) || 
                                tool.descripcion.toLowerCase().includes(searchTerm) ||
                                tool.tags.some(t => t.toLowerCase().includes(searchTerm));
            const matchesCategory = activeCategory === 'all' || tool.categoria === activeCategory;
            return matchesSearch && matchesCategory;
        });

        renderTools(filtered);
    }

    searchBar.addEventListener('input', filterTools);
});
