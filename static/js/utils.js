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

function postMethod(jsonBody){
  return {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(jsonBody),
  }
}

function getCardElement(currentElement) {
  if (currentElement.dataset.hasOwnProperty('product'))
    return currentElement;
  else if (currentElement.parentElement === null)
    return null;

  return getCardElement(currentElement.parentElement);
}

function iconToLoading(icon) {
  const oldClasses = [];
  const loadingClasses = ['fas', 'fa-spinner', 'fa-pulse'];
  icon.classList.forEach((className) => {
    if(className.startsWith("fa")){
      oldClasses.push(className);
      icon.classList.remove(className);
    }
  });

  icon.classList.add(...loadingClasses);

  // undo function
  return () => {
    icon.classList.remove('fa-spinner', 'fa-pulse');
    icon.classList.add(...oldClasses);
  }
  
}

