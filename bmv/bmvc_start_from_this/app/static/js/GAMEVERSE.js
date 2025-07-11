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

document.addEventListener('DOMContentLoaded', () => {
    const loginBtn = document.getElementById('login-btn');
    const loginModal = document.getElementById('login-modal');
    const closeBtn = document.getElementById('close-btn');

    // Função para mostrar o modal de login
    const showLoginModal = () => {
        if (loginModal) {
            loginModal.classList.remove('hidden');
        }
    };

    // Função para esconder o modal de login
    const hideLoginModal = () => {
        if (loginModal) {
            loginModal.classList.add('hidden');
        }
    };

    // --- NOVA IMPLEMENTAÇÃO ---
    // Verifica se a URL contém o parâmetro para mostrar o login
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('login') === 'true') {
        showLoginModal();
    }
    // --- FIM DA NOVA IMPLEMENTAÇÃO ---

    // Adiciona evento para o botão "Entrar" no cabeçalho
    if (loginBtn) {
        loginBtn.addEventListener('click', showLoginModal);
    }

    // Adiciona evento para o botão de fechar ("X") do modal
    if (closeBtn) {
        closeBtn.addEventListener('click', hideLoginModal);
    }

    // Adiciona evento para fechar o modal se o usuário clicar fora da caixa de conteúdo
    if (loginModal) {
        loginModal.addEventListener('click', (event) => {
            if (event.target === loginModal) {
                hideLoginModal();
            }
        });
    }
});
