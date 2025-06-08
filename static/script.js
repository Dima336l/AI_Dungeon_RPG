document.addEventListener('DOMContentLoaded', () => {
  const startBtn = document.getElementById('start-btn');
  const sceneElem = document.getElementById('scene-text');
  const choicesElem = document.getElementById('choices');
  const fullText = window.sceneText;
  const optionsData = window.optionsData;
  const beep = new Audio(window.beepUrl);

  function typeText(element, text, speed = 30, callback) {
    let index = 0;
    element.textContent = '';

    function type() {
      if (index < text.length) {
        element.textContent += text.charAt(index);
        if (text.charAt(index).match(/[a-z0-9]/i)) {
          beep.currentTime = 0;
          beep.play();
        }
        index++;
        setTimeout(type, speed);
      } else if (callback) {
        callback();
      }
    }

    type();
  }

  // Keyboard shortcut for choices 1-9
  document.addEventListener('keydown', (e) => {
    if (e.key >= '1' && e.key <= '9') {
      const choice = e.key;
      const optionBtn = choicesElem.querySelector(`button[data-option="${choice}"]`);
      if (optionBtn) {
        optionBtn.click();
      }
    }
  });

  startBtn.addEventListener('click', () => {
    startBtn.style.display = 'none';

    typeText(sceneElem, fullText, 30, () => {
      choicesElem.innerHTML = '';
      for (const [num, option] of Object.entries(optionsData)) {
        const btn = document.createElement('button');
        btn.className = 'choice-btn';
        btn.setAttribute('data-option', num);
        btn.textContent = `${num}. ${option}`;
        btn.addEventListener('click', () => {
          fetch("/", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `choice=${num}`
          }).then(() => {
            window.location.reload();
          });
        });
        choicesElem.appendChild(btn);
      }
    });
  });
});
