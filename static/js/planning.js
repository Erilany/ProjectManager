document.addEventListener('DOMContentLoaded', function() {
    const slider = document.getElementById('timelineSlider');
    const tableContainer = document.querySelector('.table-responsive');
    
    if (!tableContainer) {
        console.error('Container de tableau non trouvé');
        return;
    }

    // Calculer la largeur pour une année (365 jours * 40px par jour + 250px pour la colonne fixe)
    const table = document.querySelector('.planning-table');
    const cellWidth = 40;
    const yearWidth = (365 * cellWidth) + 250;
    table.style.minWidth = `${yearWidth}px`;
    
    // Debug
    console.log('Table dimensions:', {
        yearWidth,
        actualWidth: table.offsetWidth,
        containerWidth: tableContainer.clientWidth
    });

    function updateScroll() {
        const maxScroll = tableContainer.scrollWidth - tableContainer.clientWidth;
        const scrollPosition = Math.floor((maxScroll * slider.value) / 100);
        tableContainer.scrollLeft = scrollPosition;
        
        console.log('Scroll update:', {
            maxScroll,
            scrollPosition,
            currentScroll: tableContainer.scrollLeft
        });
    }

    slider.addEventListener('input', updateScroll);
    updateScroll();
}); 