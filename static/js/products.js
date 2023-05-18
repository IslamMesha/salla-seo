const productIcons = document.querySelectorAll(".product i");

function getTakeOrLeaveElement(textElement, oldText, prompt_id){
  // NOTE textElement already has the new text

  const elm = createElement(`
    <div class="prompt-confirmation flex justify-center space-x-2 space-x-reverse mt-2 mb-4">
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
      .catch((error) => 
        iziToast.error({ title: 'Error', message: 'Can\'t save into salla.', position: 'topRight' })
      )
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
            <button class="set-description bg-red-500 hover:bg-red-700 text-white text-sm font-bold px-2 py-1 rounded mt-1">أستخدم هذا</button>
        </div>
    `);

  if (description.meta.keywords) {
    descriptionElement.appendChild(
      createElement(`
        <span class="text-gray-500 text-sm block font-bold flex flex-row-reverse mt-3">
          ${description.meta.keywords}
        </span>
      `)
    );
  }

  return descriptionElement;
}

function confirmOrCancelAllPromptsInCardButtons(){
  const elm = createElement(`
    <div class="prompt-confirmation-all flex justify-center space-x-2 space-x-reverse mt-2 mb-4">
      <button type="button" class="accept-all w-6 h-6 text-xs text-white bg-green-500 rounded hover:bg-green-600 focus:outline-none">
        <i class="fas fa-check"></i>
      </button>
      <button type="button" class="cancelled-all w-6 h-6 text-xs text-white bg-red-500 rounded hover:bg-red-600 focus:outline-none">
        <i class="fas fa-times"></i>
      </button>
    </div>
  `);

  elm.querySelector('.accept-all').addEventListener('click', () => {
    const cardElement = getCardElement(elm);

    cardElement.querySelectorAll('.accept').forEach(button => {
      button.click();
    });
    elm.remove();
  });

  elm.querySelector('.cancelled-all').addEventListener('click', () => {
    const cardElement = getCardElement(elm);

    cardElement.querySelectorAll('.cancelled').forEach(button => {
      button.click();
    });

    elm.remove();
  });

  return elm;
}

function confirmOrCancelEditingTextManuallyButtons(confirmMethod, cancelMethod){
  const elm = createElement(`
    <div class="prompt-confirmation-editing flex justify-center space-x-2 space-x-reverse mt-2 mb-2">
      <button type="button" class="accept-edits w-6 h-6 text-xs text-white bg-green-500 rounded hover:bg-green-600 focus:outline-none">
        <i class="fas fa-check"></i>
      </button>
      <button type="button" class="cancelled-edits w-6 h-6 text-xs text-white bg-red-500 rounded hover:bg-red-600 focus:outline-none">
        <i class="fas fa-times"></i>
      </button>
    </div>
  `);

  elm.querySelector('.accept-edits').addEventListener('click', () => {
    confirmMethod();
    elm.remove();
  });
  elm.querySelector('.cancelled-edits').addEventListener('click', () => {
    cancelMethod();
    elm.remove();
  });

  return elm;
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
      .catch((error) => 
        iziToast.error({ title: 'Error', message: 'Can\'t save into salla.', position: 'topRight' })
      )
      .finally(() => undo());
  });
}

productIcons.forEach((icon) => {
  icon.addEventListener("click", () => {
    const isAlreadyClicked = icon.classList.contains("fa-spinner");
    const isListHistory = icon.classList.contains("fa-history");
    const isAskGPTAction = icon.classList.contains("fa-magic");
    const isEditAllAction = icon.classList.contains("fa-paper-plane");
    const isEditAction = icon.classList.contains("fa-edit");

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
        .catch((error) => 
          iziToast.error({ title: 'Error', message: 'Can\'t get history.', position: 'topRight' })
        )
        .finally(() => iconUnloading());
    } else if (isAskGPTAction) {
      const cardElement = getCardElement(icon);
      const keywordsElement = cardElement.querySelector('.keywords-input');
      const keywords = keywordsElement.querySelector('input[type="text"]').value;
      let { product, askGptUrl } = cardElement.dataset
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

      fetch(askGptUrl, request)
        .then((response) => response.json())
        .then(({ answer, prompt_id }) => {
          const oldText = textElement.innerText;

          textElement.innerText = answer;
          icon.parentElement.appendChild(
            getTakeOrLeaveElement(textElement, oldText, prompt_id)
          );
        })
        .catch((error) => 
          iziToast.error({ title: 'Error', message: 'Unexpected error happened.', position: 'topRight' })
        )
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
          setTimeout(() => {
            if(cardElement.querySelector('.prompt-confirmation')){
              keywordsElement.appendChild(confirmOrCancelAllPromptsInCardButtons())
            }
          }, 200);
        }

      }, 200);
    } else if (isEditAction) {
      const cardElement = getCardElement(icon);
      const textElement = icon.parentElement.querySelector('p');
      const { promptType } = icon.parentElement.dataset;
      const oldText = textElement.innerText;
      const editableElement = createElement(`
      <div>
        <textarea class="block border-2 mt-3 px-3 py-2 w-full text-sm">${oldText.replace(/✅$/, '').trim()} </textarea>
      </div>
      `);

      textElement.replaceWith(editableElement);
      editableElement.querySelector('textarea').focus();
      editableElement.querySelector('textarea').setSelectionRange(oldText.length, oldText.length);
      editableElement.appendChild(
        confirmOrCancelEditingTextManuallyButtons(
          // confirm
          () => {
            const newText = editableElement.querySelector('textarea').value;
            const cardElement = getCardElement(editableElement);
            let { product, sallaSubmitManuallyUrl } = cardElement.dataset;
            product = JSON.parse(product);
            const request = postMethod({
              product_id: product.id,
              prompt_type: promptType,
              new_value: newText.trim(),
            });
        
            fetch(sallaSubmitManuallyUrl, request)
              .then((response) => response.json())
              .then(({ new_value }) => {
                textElement.innerText = new_value;
                editableElement.replaceWith(textElement);
              })
              .catch((error) => 
                iziToast.error({ title: 'Error', message: 'Can\'t save into salla.', position: 'topRight' })
              )
              .finally(() => {
                iconUnloading();
              });
          },


          // cancel
          () => {
            editableElement.replaceWith(textElement);
            iconUnloading();
          }
        )
      );
      
      // let { product, askGptUrl } = cardElement.dataset
      // product = JSON.parse(product);
      // const request = postMethod({
      //   product_id: product.id,
      //   // NOTE this may cause issue when user edit the product but not refresh the page
      //   product_name: product.name,
      //   product_description: product.description,
      //   product_seo_title: product.metadata.title,
      //   brand_name: product.brand,
      //   // more data
      //   prompt_type: promptType,
      // })

      // fetch(askGptUrl, request)
      //   .then((response) => response.json())
      //   .then(({ answer, prompt_id }) => {
      //     const oldText = textElement.innerText;

      //     textElement.innerText = answer;
      //     icon.parentElement.appendChild(
      //       getTakeOrLeaveElement(textElement, oldText, prompt_id)
      //     );
      //   })
      //   .catch((error) => 
      //     iziToast.error({ title: 'Error', message: 'Unexpected error happened.', position: 'topRight' })
      //   )
      //   .finally(() => {
      //     iconUnloading();
      //   });
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


