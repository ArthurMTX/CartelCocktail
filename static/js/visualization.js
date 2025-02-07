document.addEventListener('DOMContentLoaded', function() {
    // Configuration
    const width = document.querySelector('.network-visualization').clientWidth;
    const height = document.querySelector('.network-visualization').clientHeight;
    
    // Créer le SVG
    const svg = d3.select('#network')
        .attr('width', width)
        .attr('height', height);

    // Configuration de la simulation
    const simulation = d3.forceSimulation()
        .force('link', d3.forceLink().id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(50));

    // Charger les données
    fetch('/api/visualization-data')
        .then(response => response.json())
        .then(data => {
            // Créer les éléments du graphique
            const link = svg.append('g')
                .selectAll('line')
                .data(data.links)
                .enter().append('line')
                .attr('class', 'link')
                .style('stroke', d => d3.interpolateViridis(d.value))
                .style('stroke-width', d => Math.sqrt(d.value) * 2);

            const node = svg.append('g')
                .selectAll('.node')
                .data(data.nodes)
                .enter().append('g')
                .attr('class', 'node')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));

            node.append('circle')
                .attr('r', d => d.type === 'genre' ? 8 : 12)
                .style('fill', d => d.type === 'genre' ? '#d4af37' : '#e74c3c');

            node.append('text')
                .attr('dx', 15)
                .attr('dy', 5)
                .text(d => d.name)
                .style('fill', '#ffffff')
                .style('font-size', '12px');

            // Ajouter des titres au survol
            node.append('title')
                .text(d => d.name);

            // Mise à jour de la simulation
            simulation
                .nodes(data.nodes)
                .on('tick', ticked);

            simulation.force('link')
                .links(data.links);

            // Fonction de mise à jour des positions
            function ticked() {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);

                node
                    .attr('transform', d => `translate(${d.x},${d.y})`);
            }

            // Gestion du zoom
            const zoom = d3.zoom()
                .scaleExtent([0.5, 4])
                .on('zoom', (event) => {
                    svg.selectAll('g').attr('transform', event.transform);
                });

            svg.call(zoom);
        });

    // Fonctions de drag & drop
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    // Gestion des boutons de filtrage
    document.getElementById('showAll').addEventListener('click', () => {
        d3.selectAll('.node').style('opacity', 1);
        d3.selectAll('.link').style('opacity', 0.6);
    });

    document.getElementById('showGenres').addEventListener('click', () => {
        d3.selectAll('.node').style('opacity', d => d.type === 'genre' ? 1 : 0.2);
        d3.selectAll('.link').style('opacity', 0.2);
    });

    document.getElementById('showCocktails').addEventListener('click', () => {
        d3.selectAll('.node').style('opacity', d => d.type === 'cocktail' ? 1 : 0.2);
        d3.selectAll('.link').style('opacity', 0.2);
    });
});
