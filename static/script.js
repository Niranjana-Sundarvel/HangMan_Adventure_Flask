const $ = id => document.getElementById(id);
const screens = ["welcomeScreen", "categoryScreen", "difficultyScreen", "gameScreen", "resultScreen"];
let category = "Animals";
let level = "easy";
let soundOn = true;
let finished = false;
let currentState = null;

function show(id) {
  screens.forEach(screen => $(screen).classList.toggle("hidden", screen !== id));
}
function toast(message) {
  $("toast").textContent = message;
  $("toast").classList.add("show");
  setTimeout(() => $("toast").classList.remove("show"), 1800);
}
async function api(url, body = null) {
  const options = { method: body === null ? "GET" : "POST", headers: {} };
  if (body !== null) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok || data.ok === false) throw new Error(data.message || "Something went wrong.");
  return data;
}
function renderCategories() {
  const icons = {
    Animals:"🐾", Fruits:"🍎", Vegetables:"🥕", Countries:"🌍",
    Sports:"🏆", Technology:"💻", Flowers:"🌸", Vehicles:"🚗"
  };
  $("categoryGrid").innerHTML = Object.entries(icons).map(([name, emoji]) =>
    `<button class="category-card ${name === category ? "selected" : ""}" data-category="${name}">
      <span class="emoji">${emoji}</span><b>${name}</b>
    </button>`
  ).join("");
  document.querySelectorAll(".category-card").forEach(button => {
    button.addEventListener("click", () => {
      category = button.dataset.category;
      renderCategories();
    });
  });
}
function renderLevelSelection() {
  document.querySelectorAll(".difficulty").forEach(button => {
    button.classList.toggle("selected", button.dataset.level === level);
  });
}
function beep(frequency, duration) {
  try {
    const context = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = context.createOscillator();
    const gain = context.createGain();
    oscillator.frequency.value = frequency;
    gain.gain.value = .04;
    oscillator.connect(gain);
    gain.connect(context.destination);
    oscillator.start();
    oscillator.stop(context.currentTime + duration / 1000);
    oscillator.onended = () => context.close();
  } catch (error) {
    // Sound is optional; the game still works if browser audio is unavailable.
  }
}
function updateGame(state) {
  currentState = state;
  finished = state.finished;
  $("categoryLabel").textContent = `${state.category_emoji} ${state.category}`;
  $("levelLabel").textContent = state.level.charAt(0).toUpperCase() + state.level.slice(1);
  $("livesLabel").textContent = state.lives;
  $("hintText").textContent = `Hint: ${state.hint}`;
  $("wordDisplay").innerHTML = state.word_display.map(letter =>
    `<span class="letter-slot">${letter}</span>`
  ).join("");
  $("message").textContent = state.finished
    ? (state.won ? "Excellent guessing! You found the hidden word." : "No chances left. Try another word!")
    : "Choose a letter to reveal the word.";

  $("keyboard").innerHTML = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").map(letter => {
    const used = state.guessed.includes(letter);
    const kind = used ? (state.word_display.includes(letter) ? "correct" : "wrong") : "";
    return `<button class="key ${kind}" data-letter="${letter}" ${used || state.finished ? "disabled" : ""}>${letter}</button>`;
  }).join("");
  document.querySelectorAll(".key").forEach(button => {
    button.addEventListener("click", () => guess(button.dataset.letter));
  });

  ["head", "body", "leftArm", "rightArm", "leftLeg", "rightLeg"].forEach((id, index) => {
    $(id).style.visibility = state.mistakes > index ? "visible" : "hidden";
  });
  $("againBtn").disabled = !state.finished;
}
async function startRound() {
  try {
    const data = await api("/api/start", { category, level });
    updateGame(data.state);
    show("gameScreen");
  } catch (error) {
    toast(error.message);
  }
}
async function guess(letter) {
  if (finished) return;
  try {
    const before = currentState ? currentState.mistakes : 0;
    const data = await api("/api/guess", { letter });
    updateGame(data.state);
    if (data.state.mistakes > before) {
      if (soundOn) beep(180, 90);
    } else if (soundOn) {
      beep(520, 70);
    }
    if (data.state.finished) showResult(data.state);
  } catch (error) {
    toast(error.message);
  }
}
function showResult(state) {
  $("resultIcon").textContent = state.won ? "🎉" : "🌻";
  $("resultTitle").textContent = state.won ? "You did it!" : "Nice try!";
  $("resultText").textContent = state.won
    ? "Excellent guessing! You found the hidden word."
    : "Don't give up. Try another word and improve your guessing!";
  $("answerWord").textContent = state.answer;
  show("resultScreen");
  if (soundOn && state.won) beep(700, 180);
}
async function playAnotherRound() {
  try {
    const data = await api("/api/new-round", {});
    updateGame(data.state);
    show("gameScreen");
  } catch (error) {
    toast(error.message);
  }
}

$("startBtn").onclick = () => { renderCategories(); show("categoryScreen"); };
$("categoryNext").onclick = () => { renderLevelSelection(); show("difficultyScreen"); };
document.querySelectorAll("[data-back]").forEach(button => {
  button.onclick = () => show(button.dataset.back);
});
document.querySelectorAll(".difficulty").forEach(button => {
  button.onclick = () => {
    level = button.dataset.level;
    renderLevelSelection();
  };
});
$("playBtn").onclick = startRound;
$("restartBtn").onclick = startRound;
$("againBtn").onclick = playAnotherRound;
$("resultPlayBtn").onclick = playAnotherRound;
$("changeCategoryBtn").onclick = () => { renderCategories(); show("categoryScreen"); };
$("homeBtn").onclick = async () => {
  try { await api("/api/reset", {}); } catch (error) {}
  category = "Animals";
  level = "easy";
  currentState = null;
  finished = false;
  show("welcomeScreen");
};
$("soundToggle").onclick = () => {
  soundOn = !soundOn;
  $("soundToggle").textContent = soundOn ? "🔊" : "🔇";
  toast(soundOn ? "Sound on" : "Sound off");
};
$("settingsBtn").onclick = () => toast("Use the speaker button to turn sound on or off.");
renderCategories();
renderLevelSelection();
