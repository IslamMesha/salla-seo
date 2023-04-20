function createElement(html) {
  const div = document.createElement("div");
  div.innerHTML = html;
  return div.firstElementChild;
}

function buttonToLoading(button) {
  const oldText = button.innerText;
  button.innerText = "Loading...";
  button.disabled = true;
  button.classList.add("cursor-not-allowed", "opacity-50");

  // return undo function
  return () => {
    button.innerText = oldText;
    button.disabled = false;
    button.classList.remove("cursor-not-allowed", "opacity-50");
  };
}

function resetTextInputField(textInputField) {
  textInputField.value = "";
  textInputField.focus();
}
