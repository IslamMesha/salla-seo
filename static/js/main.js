const products = document.querySelectorAll('.product')
products.forEach(product => {
    product.setAttribute('dir', 'auto')
})

document.addEventListener('DOMContentLoaded', () => {
    const loadingPage = document.querySelector('#loading-page')
    loadingPage.remove();
});
