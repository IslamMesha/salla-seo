const getDescriptionButtons = document.querySelectorAll("button[data-product]");
const deleteKeywordButtons = document.querySelectorAll(".delete-keyword");
const addKeywordButtons = document.querySelectorAll(".add-keyword");
const productIcons = document.querySelectorAll(".product i");


function createDeleteKeywordButton() {
  const deleteKeywordButton = document.createElement("span");
  const classes = [
    "delete-keyword",
    "rounded",
    "inline-block",
    "text-white",
    "font-bold",
    "bg-red-500",
    "hover:bg-red-700",
    "cursor-pointer",
    "w-4",
    "text-center",
    "ml-1",
  ];

  deleteKeywordButton.classList.add(...classes);
  deleteKeywordButton.innerHTML = "&times;";

  return deleteKeywordButton;
}

function createKeywordElement(keyword) {
  const keywordElement = document.createElement("span");
  const classes = [
    "keyword",
    "text-sm",
    "text-center",
    "px-1",
    "py-1",
    "bg-yellow-300",
    "rounded",
    "font-bold",
    "mr-1",
    "mb-1",
    "inline-block",
  ];

  keywordElement.classList.add(...classes);
  keywordElement.innerText = keyword;

  return keywordElement;
}

function getKeywords(keywordsElement) {
  return Array.from(keywordsElement.querySelectorAll(".keyword")).map(
    (keyword) => keyword.firstChild.textContent.trim()
  );
}

function addKeyword(keyword, keywordsElement) {
  const keywordElement = createKeywordElement(keyword);
  const deleteKeywordButton = createDeleteKeywordButton();
  keywordElement.appendChild(deleteKeywordButton);
  keywordsElement.appendChild(keywordElement);

  deleteKeywordButton.addEventListener("click", () =>
    deleteKeywordButton.parentElement.remove()
  );
}

function createDescriptionPopupListItem(description) {
  const descriptionElement = createElement(`
        <div class="description-item mb-8 pb-5 border-b-2 border-solid">
            <span>${description.chat_gpt_log.answer}</span>
            <button class="set-description bg-red-500 hover:bg-red-700 text-white text-sm font-bold px-2 py-1 rounded mt-1">Set This Description</button>
        </div>
    `);

  if (description.meta.keywords_str) {
    const keywordsElement = document.createElement("span");

    keywordsElement.innerText = description.meta.keywords_str;
    keywordsElement.classList.add(
      "text-gray-500",
      "text-sm",
      "block",
      "font-bold",
      "flex",
      "flex-row-reverse",
      "mt-3"
    );
    descriptionElement.appendChild(keywordsElement);
  }

  return descriptionElement;
}

function addEventToSetDescriptionButton(
  setDescriptionButton,
  textElement,
  productId,
  description
) {
  setDescriptionButton.addEventListener("click", () => {
    const undo = buttonToLoading(setDescriptionButton);
    const setDescriptionUrl = `/salla/write-description/${productId}/`;

    fetch(setDescriptionUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description }),
    })
      .then((response) => response.json())
      .then((data) => {
        textElement.innerText = description;
        closePopup(listDescriptionLogPopup);
        setDescriptionButton.remove();
      })
      .catch((error) => console.log(error))
      .finally(() => undo());
  });
}

getDescriptionButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const undo = buttonToLoading(button);
    const cardElement = button.parentElement.parentElement;
    const url = "{% url 'app:ask_for_description' %}";
    const keywordsElement = cardElement.querySelector(
      ".keywords div:first-child"
    );
    const product = JSON.parse(button.getAttribute("data-product"));
    const request = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...product,
        keywords_list: getKeywords(keywordsElement),
      }),
    };

    fetch(url, request)
      .then((response) => response.json())
      .then((data) => {
        const descriptionElement = cardElement.querySelector(
          ".product-description"
        );
        const setDescriptionButton = createElement(`
                    <button class="set-description bg-red-500 hover:bg-red-700 text-white text-sm font-bold px-2 py-1 rounded mt-1">Set This Description</button>
                `);
        const description = data.description;

        descriptionElement.innerText = data.description;
        descriptionElement.parentElement.appendChild(setDescriptionButton);

        addEventToSetDescriptionButton(
          setDescriptionButton,
          description,
          product.id,
          cardElement
        );
      })
      .catch((error) => console.log(error))
      .finally(() => undo());
  });
});

deleteKeywordButtons.forEach((button) =>
  button.addEventListener("click", () => button.parentElement.remove())
);

addKeywordButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const inputField = button.previousElementSibling;
    const keyword = inputField.value;
    const keywordsElement =
      button.parentElement.parentElement.parentElement.querySelector(
        ".keywords div:first-child"
      );
    const keywordsArray = getKeywords(keywordsElement);

    if (keywordsArray.includes(keyword)) {
      resetTextInputField(inputField);
      return;
    }

    addKeyword(keyword, keywordsElement);
    resetTextInputField(inputField);
  });
});

productIcons.forEach((icon) => {
  icon.addEventListener("click", () => {
    const isAlreadyClicked = icon.classList.contains("opacity-50");
    const isListHistory = icon.classList.contains("fa-history");
    if (isAlreadyClicked || !isListHistory)
      return;

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
          const descriptionText = setDescriptionButton.parentElement.firstElementChild.innerText;
          const textElement = icon.parentElement.querySelector('p');

          popup.appendChild(descriptionElement);
          addEventToSetDescriptionButton(
            setDescriptionButton,
            textElement,
            product.id,
            descriptionText,
          );
        });
      })
      .catch((error) => console.log(error))
      .finally(() => icon.classList.remove('opacity-50'));
  });
});
