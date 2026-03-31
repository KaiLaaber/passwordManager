
async function generatePassword(){
    const res = await fetch("http://127.0.0.1:5000/generate-password")
    const data = await res.json()
    
    document.getElementById('generatedPassword').innerText = data.password
}

async function addPassword(){
    const site = document.getElementById('site').value
    const username = document.getElementById('username').value
    const password = document.getElementById('password').value

    const res = await fetch("http://127.0.0.1:5000/passwords", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ site, username, password })
    })

    const data = await res.json()
    console.log(data)
}

async function getPasswords(){
    const res = await fetch("http://127.0.0.1:5000/passwords", {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    })

    const data = await res.json()
    console.log(data)
}

async function loadPasswords(){
    const res = await fetch("http://127.0.0.1:5000/passwords", {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    });
    const data = await res.json()

    const passwordList = document.getElementById('passwordList')
    passwordList.innerHTML = '';

    data.forEach(item => {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${item.site}</strong> | ${item.username} | ${item.password}`;
        passwordList.appendChild(li);
    });
    
    displayPasswords();
}

function displayPasswords(){
    const passwordList = document.getElementById('passwordList');
    passwordList.style.display = 'block';
}

window.onload = loadPasswords();