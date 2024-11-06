document.getElementById('article-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const subject = document.getElementById('subject').value;

    if (!subject) {
        alert('Veuillez entrer un sujet');
        return;
    }

    const response = await fetch('/generate-article', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ subject: subject })
    });

    const data = await response.json();
    if (data.article) {
        document.getElementById('article-content').innerHTML = data.article;
    } else {
        alert('Erreur lors de la génération de l\'article');
    }
});
