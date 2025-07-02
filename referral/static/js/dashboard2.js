  function copyToClipboard(elementId) {
    const text = document.getElementById(elementId).innerText;
    navigator.clipboard.writeText(text).then(() => {
      alert("Copied: " + text);
    }).catch(err => {
      console.error('Failed to copy: ', err);
    });
  }

//hamburger for settings functionality
function toggleSettingsMenu() {
  const menu = document.getElementById("settingsMenu");
  menu.classList.toggle("hidden");
}

// Simulate user logout
function logout() {
  alert("Logged out!");
  // You can redirect to login or clear session here
}

// Update username and profile photo
function updateUserDetails() {
  const usernameInput = document.getElementById("newUsername");
  const usernameDisplay = document.getElementById("username");
  const newUsername = usernameInput.value.trim();
  if (newUsername) {
    usernameDisplay.textContent = newUsername;
    usernameInput.value = '';
  }

  const photoInput = document.getElementById("profilePhoto");
  const file = photoInput.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      document.querySelector("img[alt='User Avatar']").src = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  document.getElementById("settingsMenu").classList.add("hidden");
}


//code copied functionality
// Copies only the referral code text
function copyToClipboard(codeId, btnId, originalText) {
  const text = document.getElementById(codeId).innerText;
  navigator.clipboard.writeText(text).then(() => {
    showCopiedMessageOnButton(btnId, "Code Copied!", originalText);
  });
}

// Copies the full referral link (e.g., https://yourdomain.com/register?ref=7331X)
function copyReferralLink(btnId, originalText) {
  const baseUrl = window.location.origin;
  const code = document.getElementById('referralCode').innerText;
  const link = `${baseUrl}/signup?ref=${code}`;
  navigator.clipboard.writeText(link).then(() => {
    showCopiedMessageOnButton(btnId, "Link Copied!", originalText);
  });
}

// Temporarily changes button text to success message, then reverts
function showCopiedMessageOnButton(btnId, message, originalText) {
  const btn = document.getElementById(btnId);
  const span = btn.querySelector('span');
  span.innerText = message;
  btn.disabled = true;
  setTimeout(() => {
    span.innerText = originalText;
    btn.disabled = false;
  }, 2000);
}



// share button functionality
    function toggleShareIcons() {
        const icons = document.getElementById("socialIcons");
        if (icons.classList.contains("hidden")) {
            icons.classList.remove("hidden");
            icons.classList.remove("animate-bounceOut");
            icons.classList.add("animate-bounceUp");
        } else {
            icons.classList.remove("animate-bounceUp");
            icons.classList.add("animate-bounceOut");
            setTimeout(() => {
                icons.classList.add("hidden");
            }, 400); // match animation duration
        }
    }




// Example leaderboard data
/*const leaderboardData = [
    { name: "Kelvin", referrals: 34 },
    { name: "Amina", referrals: 27 },
    { name: "Kwame", referrals: 22 },
    { name: "Esi", referrals: 19 },
    { name: "Tunde", referrals: 15 }
];
*/

// Toggle modal visibility
function toggleLeaderboardModal() {
    const modal = document.getElementById("leaderboardModal");
    modal.classList.toggle("hidden");
    if (!modal.classList.contains("hidden")) {
        loadLeaderboard(); // Load data when opening
    }
}


// Render leaderboard
//function loadLeaderboard() {
/*  const tbody = document.getElementById("leaderboardBody");
    tbody.innerHTML = ""; // Clear previous content

    leaderboardData.forEach((user, index) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td class="py-3 px-4 font-bold">${index + 1}</td>
            <td class="py-3 px-4">${user.name}</td>
            <td class="py-3 px-4">${user.referrals}</td>
        `;
        tbody.appendChild(row);
    });
//}
//*/











/*
  document.addEventListener("DOMContentLoaded", function () {
    fetch('/api/user-profile/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken') // Only needed for POST or if you require CSRF for authenticated GET
      },
      credentials: 'include' // include cookies for session-authenticated users
    })
    .then(response => {
      if (!response.ok) {
        throw new Error("Failed to fetch user data");
      }
      return response.json();
    })
      */
    /* .then(data => {
      // Inject into HTML
     document.getElementById('username').textContent = data.username;
      document.getElementById('userEmail').textContent = data.email;
      document.getElementById('referralPoints').textContent = data.referral_points;
      document.getElementById('referralCode').textContent = data.referral_code;
      document.getElementById('userRank').textContent = `#${data.rank}`;
    })
    .catch(error => {
      console.error("Error loading user data:", error);
    });
    */

    // Optional: Get CSRF token if you're doing POST/PUT requests
  /*  function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
  });
  */
