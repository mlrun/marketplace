/*
Copyright 2021 Iguazio Systems Ltd.

Licensed under the Apache License, Version 2.0 (the "License") with
an addition restriction as set forth herein. You may not use this
file except in compliance with the License. You may obtain a copy of
the License at http://www.apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing
permissions and limitations under the License.

In addition, you may not use the software for any purposes that are
illegal under applicable law, and the grant of the foregoing license
under the Apache 2.0 license is conditioned upon your compliance with
such restriction.
*/
var initToggleItems = () => {
  var itemsToToggle = document.querySelectorAll(togglebuttonSelector);
  console.log(itemsToToggle, togglebuttonSelector)
  // Add the button to each admonition and hook up a callback to toggle visibility
  itemsToToggle.forEach((item, index) => {
    var toggleID = `toggle-${index}`;
    var buttonID = `button-${toggleID}`;
    var collapseButton = `
      <button id="${buttonID}" class="toggle-button" data-target="${toggleID}" data-button="${buttonID}">
          <div class="bar horizontal" data-button="${buttonID}"></div>
          <div class="bar vertical" data-button="${buttonID}"></div>
      </button>`;

    item.setAttribute('id', toggleID);

    if (!item.classList.contains("toggle")){
      item.classList.add("toggle");
    }

    // If it's an admonition block, then we'll add the button inside
    if (item.classList.contains("admonition")) {
      item.insertAdjacentHTML("afterbegin", collapseButton);
    } else {
      item.insertAdjacentHTML('beforebegin', collapseButton);
    }

    thisButton = $(`#${buttonID}`);
    thisButton.on('click', toggleClickHandler);
    if (!item.classList.contains("toggle-shown")) {
      toggleHidden(thisButton[0]);
    }
  })
};

// This should simply add / remove the collapsed class and change the button text
var toggleHidden = (button) => {
  target = button.dataset['target']
  var itemToToggle = document.getElementById(target);
  if (itemToToggle.classList.contains("toggle-hidden")) {
    itemToToggle.classList.remove("toggle-hidden");
    button.classList.remove("toggle-button-hidden");
  } else {
    itemToToggle.classList.add("toggle-hidden");
    button.classList.add("toggle-button-hidden");
  }
}

var toggleClickHandler = (click) => {
  button = document.getElementById(click.target.dataset['button']);
  toggleHidden(button);
}

// If we want to blanket-add toggle classes to certain cells
var addToggleToSelector = () => {
  const selector = "";
  if (selector.length > 0) {
    document.querySelectorAll(selector).forEach((item) => {
      item.classList.add("toggle");
    })
  }
}

// Helper function to run when the DOM is finished
const sphinxToggleRunWhenDOMLoaded = cb => {
  if (document.readyState != 'loading') {
    cb()
  } else if (document.addEventListener) {
    document.addEventListener('DOMContentLoaded', cb)
  } else {
    document.attachEvent('onreadystatechange', function() {
      if (document.readyState == 'complete') cb()
    })
  }
}
sphinxToggleRunWhenDOMLoaded(addToggleToSelector)
sphinxToggleRunWhenDOMLoaded(initToggleItems)
