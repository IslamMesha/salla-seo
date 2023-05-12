const productIcons = document.querySelectorAll(".product i");

function getTakeOrLeaveElement(textElement, oldText, prompt_id){
  // NOTE textElement already has the new text

  const elm = createElement(`
    <div class="prompt-confirmation flex justify-center space-x-2 space-x-reverse mb-4">
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
    let { sallaSubmitUrl } = cardElement.dataset;

    fetch(sallaSubmitUrl, postMethod({ prompt_id }))
      .catch((error) => console.error(error))
      .finally(() => elm.remove());
  });

  elm.querySelector('.cancelled').addEventListener('click', () => {
    const cardElement = getCardElement(textElement);
    const { promptDeclineUrl } = cardElement.dataset;

    fetch(promptDeclineUrl, postMethod({ prompt_id }))
      .catch((error) => console.error(error))
      .finally(() => elm.remove());

    if(oldText){
      textElement.innerText = oldText;
      elm.remove();
    }
  });

  if(oldText){} else { elm.querySelector('.cancelled').classList.add('hidden') }
  return elm;
}

function createDescriptionPopupListItem(description) {
  const descriptionElement = createElement(`
        <div class="description-item mb-8 pb-5 border-b-2 border-solid">
            <span>${description.chat_gpt_response.answer}</span>
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
    const undo = buttonToLoading(button);
    const cardElement = getCardElement(textElement);
    let { product, sallaSubmitUrl } = cardElement.dataset;

    product = JSON.parse(product);
    const request = postMethod({
      product_id: product.id,
      prompt_type: textElement.parentElement.dataset.promptType,
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
    const isAlreadyClicked = icon.classList.contains("fa-spinner");
    const isListHistory = icon.classList.contains("fa-history");
    const isEditAction = icon.classList.contains("fa-magic");
    const isEditAllAction = icon.classList.contains("fa-paper-plane");

    if (isAlreadyClicked)
      return;

    const iconUnloading = iconToLoading(icon)

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
        .finally(() => iconUnloading());
    } else if (isEditAction) {
      const cardElement = getCardElement(icon);
      const keywordsElement = cardElement.querySelector('.keywords-input');
      const keywords = keywordsElement.querySelector('input[type="text"]').value;
      let { product, editUrl } = cardElement.dataset
      const textElement = icon.parentElement.querySelector('p');
      const { promptType } = icon.parentElement.dataset;
      product = JSON.parse(product);
      const request = postMethod({
        product_id: product.id,
        // NOTE this may cause issue when user edit the product but not refresh the page
        product_name: product.name,
        product_description: product.description,
        product_seo_title: product.metadata.title,
        brand_name: product.brand,
        // more data
        keywords: keywords.trim(),
        prompt_type: promptType,
      })

      const isHasConfirmationPrompt = Boolean(icon.parentElement.querySelector('.prompt-confirmation'));

      if (isHasConfirmationPrompt) {
        iconUnloading();
        return
      }

      if (!keywords.trim()) {
        keywordsElement.querySelector('#error-msg').classList.remove('hidden');
        keywordsElement.querySelector('input[type="text"]').classList.add('border-red-500');
        iconUnloading();
        return;
      } else {
        keywordsElement.querySelector('#error-msg').classList.add('hidden');
        keywordsElement.querySelector('input[type="text"]').classList.remove('border-red-500');
      }

      fetch(editUrl, request)
        .then((response) => response.json())
        .then(({ answer, prompt_id }) => {
          const oldText = textElement.innerText;

          textElement.innerText = answer;
          icon.parentElement.appendChild(
            getTakeOrLeaveElement(textElement, oldText, prompt_id)
          );
        })
        .catch((error) => console.error(error))
        .finally(() => {
          iconUnloading();
        });

    } else if (isEditAllAction) {
      const cardElement = getCardElement(icon);
      const keywordsElement = cardElement.querySelector('.keywords-input');
      const keywords = keywordsElement.querySelector('input[type="text"]').value;

      if (!keywords.trim()) {
        keywordsElement.querySelector('#error-msg').classList.remove('hidden');
        keywordsElement.querySelector('input[type="text"]').classList.add('border-red-500');
        iconUnloading();
        return;
      } else {
        keywordsElement.querySelector('#error-msg').classList.add('hidden');
        keywordsElement.querySelector('input[type="text"]').classList.remove('border-red-500');
      }

      const notProcessedElements = cardElement.querySelectorAll('[data-is-processed="false"] .fa-magic');
      notProcessedElements.forEach( magicIcon => magicIcon.click() );
      const iconLoadingInterval = setInterval(() => {

        const isStillLoading = Array.from(notProcessedElements).filter(magicIcon => {
          return magicIcon.classList.contains('fa-spinner');
        })
        console.log(isStillLoading)
        if (isStillLoading.length > 0) return;
        else{
          iconUnloading();
          clearInterval(iconLoadingInterval);
        }

      }, 200);
    }

  });
});


document.addEventListener('DOMContentLoaded', () => {

  document.querySelectorAll('[data-is-processed="true"]').forEach(elm => {
    const textElement = elm.querySelector('p');
    textElement.appendChild(
      createElement(`<span title="Processed" class="cursor-default">✅</span>`)
    );
  });


});


