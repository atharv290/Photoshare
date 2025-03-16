document.addEventListener('DOMContentLoaded', () => {
    fetchPhotos();
});

function fetchPhotos() {
    fetch('/get_photos')
        .then(response => response.json())
        .then(photos => {
            const photoGrid = document.querySelector('.photo-grid');
            photos.forEach(photo => {
                const img = document.createElement('img');
                img.src = photo;
                photoGrid.appendChild(img);
            });
        })
        .catch(error => console.error('Error fetching photos:', error));
}
