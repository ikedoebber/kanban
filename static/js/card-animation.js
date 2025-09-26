// ===== ANIMAÇÃO DE CARDS =====

document.addEventListener('DOMContentLoaded', function() {
    console.log('Animação de cards carregada');
    
    // Adicionar animação suave aos cards
    const cards = document.querySelectorAll('.card, .task-card, .goal-card, .appointment-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});