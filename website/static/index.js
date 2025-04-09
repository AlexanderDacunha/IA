function scrollMenu(direction) {
    const container = document.querySelector('.scroll-container');
    const itemWidth = container.querySelector('.menu-item').offsetWidth + 10; // Width of one item + gap
    const scrollAmount = itemWidth * 3; // Scroll by 3 items

    if (direction === 'next') {
        container.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    } else {
        container.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    }
}
