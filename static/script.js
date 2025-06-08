document.addEventListener('DOMContentLoaded', () => {
  const startBtn = document.getElementById('start-btn');
  const sceneElem = document.getElementById('scene-text');
  const choicesElem = document.getElementById('choices');
  const beep = new Audio(window.beepUrl);

  // Declare these at top-level so accessible inside showChoices and elsewhere
  let fullText = window.sceneText;
  let optionsData = window.optionsData;

  console.log('Initial sceneText:', fullText);
  console.log('Initial optionsData:', optionsData);

  function typeText(element, text, speed = 30, callback) {
    let index = 0;
    element.textContent = '';
    console.log('Starting to type text:', text);

    function type() {
      if (index < text.length) {
        element.textContent += text.charAt(index);
        if (text.charAt(index).match(/[a-z0-9]/i)) {
          beep.currentTime = 0;
          beep.play();
        }
        index++;
        setTimeout(type, speed);
      } else {
        console.log('Finished typing text.');
        if (callback) {
          console.log('Calling callback after typing text.');
          callback();
        }
      }
    }

    type();
  }

function showChoices() {
  console.log('Clearing old choices...');
  choicesElem.innerHTML = ''; // Clear old buttons

  if (!optionsData || Object.keys(optionsData).length === 0) {
    console.log('No options available, hiding choices container.');
    choicesElem.style.display = 'none';
    return;
  } else {
    choicesElem.style.display = 'block';
  }

  console.log('Rendering new choices:', optionsData);

  for (const [num, option] of Object.entries(optionsData)) {
    console.log(`Creating button for choice ${num}: ${option}`);

    const btn = document.createElement('button');
    btn.className = 'choice-btn';
    btn.setAttribute('data-option', num);
    btn.textContent = `${num}. ${option}`;

    btn.addEventListener('click', () => {
      console.log(`Choice button clicked: ${num}`);

      // Disable all buttons immediately
      Array.from(choicesElem.children).forEach(b => b.disabled = true);

      fetch("/", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-Requested-With": "XMLHttpRequest"
        },
        body: `choice=${num}`
      })
      .then(response => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return response.json();
      })
      .then(data => {
        console.log('Fetch JSON data:', data);

        fullText = data.scene;
        optionsData = data.options;

        // Clear text & choices before typing new scene (double clear)
        sceneElem.textContent = '';
        choicesElem.innerHTML = '';

        typeText(sceneElem, fullText, 30, showChoices);

        // Update player status
        const statusElem = document.getElementById('player-status');
        if (statusElem && data.player_status) {
          statusElem.textContent = data.player_status;
        }
      })
      .catch(err => {
        console.error('Error:', err);
        // Re-enable buttons so user can retry
        Array.from(choicesElem.children).forEach(b => b.disabled = false);
      });
    });

    choicesElem.appendChild(btn);
  }
}


  // Keyboard shortcut for choices 1-9
  document.addEventListener('keydown', (e) => {
    if (e.key >= '1' && e.key <= '9') {
      const optionBtn = choicesElem.querySelector(`button[data-option="${e.key}"]`);
      if (optionBtn && !optionBtn.disabled) {
        console.log(`Keyboard shortcut pressed: ${e.key}, triggering choice click.`);
        optionBtn.click();
      }
    }
  });

  // Initially hide scene and choices
  sceneElem.style.display = 'none';
  choicesElem.style.display = 'none';

  startBtn.addEventListener('click', () => {
    console.log('Start button clicked, starting scene...');
    startBtn.style.display = 'none';       // Hide start button
    sceneElem.style.display = 'block';     // Show scene
    choicesElem.style.display = 'block';   // Show choices container

    typeText(sceneElem, fullText, 30, showChoices);
  });
});
