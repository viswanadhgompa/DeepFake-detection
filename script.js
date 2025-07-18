const dragDropArea = document.getElementById('dragDropArea');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const typeButtons = document.querySelectorAll('.type-btn');

let selectedType = 'video';

const typeAccepts = {
  video: 'video/*',
  image: 'image/*',
  audio: 'audio/*',
  text: '.txt,.doc,.docx,.pdf'
};

function updateFileInputAccept(type) {
  fileInput.accept = typeAccepts[type];
}
updateFileInputAccept(selectedType);

typeButtons.forEach(button => {
  button.addEventListener('click', () => {
    typeButtons.forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
    selectedType = button.dataset.type;
    updateFileInputAccept(selectedType);
  });
});

dragDropArea.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (event) => {
  handleFiles(event.target.files);
});

dragDropArea.addEventListener('dragover', (event) => {
  event.preventDefault();
  dragDropArea.style.backgroundColor = '#fceaea';
  dragDropArea.style.borderColor = '#8b1616';
});

dragDropArea.addEventListener('dragleave', () => {
  dragDropArea.style.backgroundColor = '';
  dragDropArea.style.borderColor = '#b22222';
});

dragDropArea.addEventListener('drop', (event) => {
  event.preventDefault();
  dragDropArea.style.backgroundColor = '';
  dragDropArea.style.borderColor = '#b22222';
  handleFiles(event.dataTransfer.files);
});

async function handleFiles(files) {
  const loadingPopup = document.getElementById('loadingPopup');
  fileList.innerHTML = '';

  if (files.length === 0) return;

  const file = files[0];  // Only process first file

  // Show loading popup
  loadingPopup.style.display = 'flex';

  try {
    // Prepare form data for upload
    const formData = new FormData();
    formData.append('file', file);

    // Send POST request to backend API
    const response = await fetch('http://127.0.0.1:8000/predict/', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const result = await response.json();
    console.log('Detection Result:', result);

    // Save result to localStorage for results page
    localStorage.setItem('deepfakeResult', JSON.stringify(result));

    // Hide loading popup
    loadingPopup.style.display = 'none';

    // Redirect to results page
    window.location.href = 'results.html';

  } catch (error) {
    loadingPopup.style.display = 'none';
    alert('Error while detecting deepfake: ' + error.message);
  }
}

const moreBtn = document.getElementById('moreBtn');
const dots = document.getElementById('dots');
const moreText = document.getElementById('more');

moreBtn.addEventListener('click', () => {
  if (dots.style.display === 'none') {
    dots.style.display = 'inline';
    moreText.style.display = 'none';
    moreBtn.textContent = 'More';
  } else {
    dots.style.display = 'none';
    moreText.style.display = 'inline';
    moreBtn.textContent = 'Less';
  }
});
function toggleModal(modalId, show) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.style.display = show ? 'flex' : 'none';
  }
}

async function login() {
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;

  try {
    const response = await fetch('http://127.0.0.1:8000/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) throw new Error('Login failed.');

    const data = await response.json();
    localStorage.setItem('token', data.access_token);
    alert('Login successful!');
    toggleModal('loginModal', false);
  } catch (err) {
    alert(err.message);
  }
}

async function signup() {
  const username = document.getElementById('signupUsername').value;
  const email = document.getElementById('signupEmail').value;
  const password = document.getElementById('signupPassword').value;

  try {
    const response = await fetch('http://127.0.0.1:8000/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    });

    if (!response.ok) throw new Error('Signup failed.');

    const data = await response.json();
    localStorage.setItem('token', data.access_token);
    alert('Signup successful!');
    toggleModal('signupModal', false);
  } catch (err) {
    alert(err.message);
  }
}
