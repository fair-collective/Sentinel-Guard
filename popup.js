async function connect() {
  chrome.identity.getAuthToken({ interactive: true }, token => {
    fetch('http://localhost:8000/connect', {
      method: 'POST',
      body: JSON.stringify({ token })
    });
    document.getElementById('status').innerText = 'Connected';
  });
}

function travel() {
  const loc = prompt("Location and days (e.g., Paris, 7):");
  fetch('http://localhost:8000/travel', {
    method: 'POST',
    body: JSON.stringify({ location: loc })
  });
}
