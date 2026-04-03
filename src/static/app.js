
async function generatePassword(){
    const res = await fetch('/generate-password')
    const data = await res.json()

    const generatedPassword = document.getElementById('generatedPassword')
    if (generatedPassword) {
        generatedPassword.innerText = data.password
    }
}

async function addPassword(){
    const site = document.getElementById('site').value
    const username = document.getElementById('username').value
    const password = document.getElementById('password').value

    const res = await fetch('/passwords', {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ site, username, password })
    })

    if (res.status === 401) {
        window.location.href = '/login'
        return
    }

    const data = await res.json()
    loadPasswords()
    console.log(data)

}

async function getPasswords(){
    const res = await fetch('/passwords', {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    })

    const data = await res.json()
    console.log(data)
}

async function loadPasswords(){
    const passwordList = document.getElementById('passwordList')
    if (!passwordList) {
        return
    }

    const res = await fetch('/passwords', {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    });

    if (res.status === 401) {
        window.location.href = '/login'
        return
    }

    const data = await res.json()

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
    if (passwordList) {
        passwordList.style.display = 'block';
    }
}

window.onload = loadPasswords;