// Basic example: Smooth scrolling for internal links
document.querySelectorAll('nav a').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        if (this.getAttribute('href').startsWith('#')) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// ========== LÓGICA DO MODAL DE LOGIN ==========

// 1. Selecionar os elementos do HTML
const loginModal = document.getElementById('login-modal');
const openLoginBtn = document.getElementById('login-btn');
const closeLoginBtn = document.getElementById('close-btn');
const loginForm = document.getElementById('login-form');

// 2. Funções para abrir e fechar o modal
const openModal = () => {
    loginModal.classList.remove('hidden');
};

const closeModal = () => {
    loginModal.classList.add('hidden');
};

// 3. Adicionar os "escutadores de evento" para os cliques
// Garante que o código não quebre se um elemento não for encontrado
if (openLoginBtn && loginModal && closeLoginBtn && loginForm) {
    
    // Abre o modal ao clicar em "Entrar"
    openLoginBtn.addEventListener('click', openModal);

    // Fecha o modal ao clicar no 'X'
    closeLoginBtn.addEventListener('click', closeModal);

    // Fecha o modal se o usuário clicar fora da caixa branca
    loginModal.addEventListener('click', (event) => {
        if (event.target === loginModal) {
            closeModal();
        }
    });

}
