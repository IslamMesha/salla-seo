const productIcons = document.querySelectorAll(".product i");
const editInput = createElement(`
  <div class="mt-2 mb-3">
    <div class="flex rounded overflow-hidden space-x-2 space-x-reverse">
      <input type="text" class="inline-block border-2 border-solid text-sm border-gray-300 w-full p-1 text-sm flex-grow outline-none rounded-lg overflow-hidden px-3" placeholder="أضف كلمات مفتاحية"/>
      <button type="submit" class="text-sm text-gray-500 hover:text-gray-700 focus:outline-none">
        <i class="fas fa-paper-plane"></i>
      </button>
      <button onclick="document.querySelector('#keyword-help-text').classList.toggle('hidden')" class="text-sm text-gray-500 hover:text-gray-700 focus:outline-none inline">
        <i class="fas fa-question"></i>
      </button>
    </div>

    <span id="keyword-help-text" class="block text-xs font-bold text-gray-400 hidden">لدقة افضل ضع كلمات مفتاحية تصف المنتج مثال : فستان, طويل, صيفي</span>
  </div>
`);

function getTakeOrLeaveElement(textElement, oldText){
  // NOTE textElement already has the new text

  const elm = createElement(`
    <div class="flex justify-center space-x-2 space-x-reverse mb-4">
      <button type="button" class="accept w-6 h-6 text-xs text-white bg-green-500 rounded hover:bg-green-600 focus:outline-none">
        <i class="fas fa-check"></i>
      </button>
      <button type="button" class="cancelled w-6 h-6 text-xs text-white bg-red-500 rounded hover:bg-red-600 focus:outline-none">
        <i class="fas fa-times"></i>
      </button>
    </div>
  `);
  elm.querySelector('.accept').addEventListener('click', () => {
    const cardElement = getCardElement(textElement);
    let { product, sallaSubmitUrl } = cardElement.dataset;
    product = JSON.parse(product);
    const request = postMethod({
      product_id: product.id,
      prompt_type: textElement.dataset.promptType,
      new_value: textElement.innerText,
    });

    fetch(sallaSubmitUrl, request)
      .then((response) => response.json())
      .then((data) => {})
      .catch((error) => console.error(error))
      .finally(() => elm.remove());
  });

  if(oldText){
    elm.querySelector('.cancelled').addEventListener('click', () => {
      textElement.innerText = oldText;
      elm.remove();
    });
  } else {
    elm.querySelector('.cancelled').classList.add('hidden')
  }

  return elm;
}

function createDescriptionPopupListItem(description) {
  const descriptionElement = createElement(`
        <div class="description-item mb-8 pb-5 border-b-2 border-solid">
            <span>${description.chat_gpt_log.answer}</span>
            <button class="set-description bg-red-500 hover:bg-red-700 text-white text-sm font-bold px-2 py-1 rounded mt-1">Set This Description</button>
        </div>
    `);

  if (description.meta.keywords_str) {
    descriptionElement.appendChild(
      createElement(`
        <span class="text-gray-500 text-sm block font-bold flex flex-row-reverse mt-3">
          ${description.meta.keywords_str}
        </span>
      `)
    );
  }

  return descriptionElement;
}

function addEventToSetDescriptionButton(button, textElement) {
  button.addEventListener("click", () => {
    const undo = buttonToLoading(setDescriptionButton);
    const cardElement = getCardElement(textElement);
    let { product, sallaSubmitUrl } = cardElement.dataset;

    product = JSON.parse(product);
    const request = postMethod({
      product_id: product.id,
      prompt_type: textElement.dataset.promptType,
      new_value: button.parentElement.querySelector('span').innerText.trim(),
    });

    fetch(sallaSubmitUrl, request)
      .then((response) => response.json())
      .then(({ new_value }) => {
        textElement.innerText = new_value;
        closePopup(listDescriptionLogPopup);
      })
      .catch((error) => console.error(error))
      .finally(() => undo());
  });
}

productIcons.forEach((icon) => {
  icon.addEventListener("click", () => {
    const isAlreadyClicked = icon.classList.contains("opacity-50");
    const isListHistory = icon.classList.contains("fa-history");
    const isEditAction = icon.classList.contains("fa-edit");
    if (isAlreadyClicked)
      return;

    icon.classList.add("opacity-50");

    if (isListHistory){
      const { promptType } = icon.parentElement.dataset;
      let { product, historyUrl } = getCardElement(icon).dataset
      product = JSON.parse(product);
  
      openPopup(listDescriptionLogPopup);
  
      fetch(historyUrl, postMethod({prompt_type: promptType, product_id: product.id }))
        .then((response) => response.json())
        .then((data) => {
          const popup = document
            .getElementById(listDescriptionLogPopup)
            .querySelector(".bg-white");
  
          popup.querySelector("h2").innerText = product.name;
          data.forEach((description) => {
            const descriptionElement = createDescriptionPopupListItem(description);
            const setDescriptionButton = descriptionElement.querySelector(".set-description");
            const textElement = icon.parentElement.querySelector('p');
  
            popup.appendChild(descriptionElement);
            addEventToSetDescriptionButton(setDescriptionButton, textElement);
          });
          if (data.length === 0) {
            const noDescriptionElement = createElement(`
                      <div class="description-item text-center text-capitalize text-3xl text-gray-400 font-bold">
                          <span>No history found</span>
                      </div>
                  `);
            popup.appendChild(noDescriptionElement);
          }
        })
        .catch((error) => console.log(error))
        .finally(() => icon.classList.remove('opacity-50'));
    } else if (isEditAction) {
      const EditingParentElement = icon.parentElement;

      EditingParentElement.appendChild(editInput)
      resetTextInputField(editInput.querySelector('input'))

      icon.classList.remove("opacity-50");
    }

  });
});

editInput.querySelector('button').addEventListener('click', () => {
  const cardElement = getCardElement(editInput);
  const textElement = editInput.parentElement.querySelector('p');

  let { product, editUrl } = cardElement.dataset
  product = JSON.parse(product);

  const request = postMethod({
    product_id: product.id,
    product_name: product.name,
    keywords: editInput.querySelector('input').value,
    prompt_type: editInput.parentElement.dataset.promptType,
  })

  fetch(editUrl, request)
    .then((response) => response.json())
    .then((data) => {
      const oldText = textElement.innerText;

      textElement.innerText = data.description;
      editInput.parentElement.appendChild(
        getTakeOrLeaveElement(textElement, oldText)
      );
    })
    .catch((error) => console.error(error))
    .finally(() => editInput.classList.add('hidden'));
});

