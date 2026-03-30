async function generatePassword(){
    const res = await fetch("http://127.0.0.1:5000/generate-password")
    const data = await res.json()
    
    document.getElementById('generatedPassword').innerText = data.password
}