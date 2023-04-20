
const loginPopupId = 'login-popup';
const listDescriptionLogPopup = 'list-description-log-popup';

function openPopup(elmId) {
  document.getElementById(elmId).style.display = "block";
}

function closePopup(elmId) {
    const popup = document.getElementById(elmId)
    popup.style.display = "none";
    popup.querySelectorAll('.description-item').forEach(elm => elm.remove())
}


