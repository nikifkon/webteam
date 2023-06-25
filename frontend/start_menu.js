
document.getElementById("reg_form").addEventListener("submit", async (evt) => {
    evt.preventDefault();
    const data = {
        name: document.getElementById('name').value,
        role: document.getElementById('role').value
    };
    const options = {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    }
    const response = await fetch('http://158.160.48.156/api/register', options);
    // const response = await fetch('http://localhost:8081/api/register', options);
    const creds = await response.json();
    localStorage.setItem('creds', JSON.stringify(creds));
    window.location.href = 'canvas.html'
});