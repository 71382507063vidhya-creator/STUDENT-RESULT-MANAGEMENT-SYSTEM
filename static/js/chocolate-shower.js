/* ============================================================
   Chocolate Shower celebration animation.

   This runs ONLY when the backend has already confirmed
   status === "PASS". It never makes any pass/fail decision itself.
   ============================================================ */

const CHOCOLATE_EMOJIS = ["🍫", "🍫", "🍬", "🍫", "🍬", "🍫"];

/**
 * Create and animate falling chocolate/candy pieces across the screen.
 * Runs for roughly 3-5 seconds, then cleans itself up.
 */
function showChocolateShower() {
  let container = document.getElementById("chocolate-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "chocolate-container";
    container.className = "chocolate-container";
    document.body.appendChild(container);
  }

  const pieceCount = 45;

  for (let i = 0; i < pieceCount; i++) {
    const piece = document.createElement("span");
    piece.className = "choco-piece";
    piece.textContent =
      CHOCOLATE_EMOJIS[Math.floor(Math.random() * CHOCOLATE_EMOJIS.length)];

    // Random horizontal position across the full width of the screen.
    piece.style.left = Math.random() * 100 + "vw";

    // Random fall duration between 3 and 5 seconds.
    const duration = 3 + Math.random() * 2;
    piece.style.animationDuration = duration + "s";

    // Small random delay so pieces don't all fall in one wave.
    piece.style.animationDelay = Math.random() * 1.2 + "s";

    // Random size for visual variety.
    const size = 1.3 + Math.random() * 1.4;
    piece.style.fontSize = size + "rem";

    container.appendChild(piece);

    // Remove each piece once its animation has finished.
    const totalLifetime = (duration + 1.2) * 1000 + 200;
    setTimeout(() => {
      if (piece.parentNode) {
        piece.parentNode.removeChild(piece);
      }
    }, totalLifetime);
  }

  // Clean up the container itself after the shower has fully finished.
  setTimeout(() => {
    if (container && container.childElementCount === 0) {
      container.remove();
    }
  }, 6500);
}

/**
 * Bind the "Celebrate Again" button. Only wires up the click handler
 * if the button exists AND the result status passed in is PASS -
 * a FAIL result should never be able to trigger this animation.
 */
function initCelebrateAgainButton(resultStatus) {
  const btn = document.getElementById("celebrate-again-btn");
  if (!btn) return;

  if (resultStatus === "PASS") {
    btn.addEventListener("click", showChocolateShower);
  } else {
    btn.style.display = "none";
  }
}
