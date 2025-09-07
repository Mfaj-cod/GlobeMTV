function toggleNav() {
  const nav = document.getElementById("nav");
  const isOpen = nav.classList.contains("open");
  nav.classList.toggle("open", !isOpen);

  // update aria-expanded
  const toggleBtn = document.querySelector(".nav-toggle");
  toggleBtn.setAttribute("aria-expanded", !isOpen);
}


document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll(".card");

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("show");
        observer.unobserve(entry.target); // prevent re-triggering
      }
    });
  }, { threshold: 0.15 });

  cards.forEach(card => observer.observe(card));
});



$(document).ready(function(){
    $('.movie-slider').slick({
        slidesToShow: 5,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 3000,
        infinite: true,
        arrows: true,
        dots: false,
        responsive: [
            { breakpoint: 1024, settings: { slidesToShow: 3 } },
            { breakpoint: 768, settings: { slidesToShow: 2 } },
            { breakpoint: 480, settings: { slidesToShow: 1 } }
        ]
    });
});

// background images
const backgrounds = [
  "https://e1.pxfuel.com/desktop-wallpaper/158/418/desktop-wallpaper-movieverse-2022-bollywood-hollywood-movies-in-dual-audio-hollywood-2022-movies-poster.jpg",

  "https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTJ8fG1vdmllfGVufDB8fDB8fHww",

  "https://c8.alamy.com/comp/M70A61/collection-of-american-movies-films-on-dvd-showing-movie-stars-film-M70A61.jpg",

  "https://i.ytimg.com/vi/qtl1jVevIVo/maxresdefault.jpg"
];

// Picking a random one
const randomBg = backgrounds[Math.floor(Math.random() * backgrounds.length)];

// Apply before using CSS variable
document.body.style.setProperty("--random-bg", `url(${randomBg})`);



document.addEventListener("DOMContentLoaded", () => {
  const trigger = document.querySelector(".select-trigger");
  const options = document.querySelector(".options");
  const hiddenInput = document.getElementById("rating");

  trigger.addEventListener("click", () => {
    options.style.display = options.style.display === "block" ? "none" : "block";
  });

  options.querySelectorAll("li").forEach(option => {
    option.addEventListener("click", () => {
      trigger.textContent = option.textContent;
      hiddenInput.value = option.dataset.value;
      options.style.display = "none";
    });
  });
});

let deferredPrompt;

window.addEventListener("beforeinstallprompt", (e) => {
  // Prevent the default mini-infobar
  e.preventDefault();
  deferredPrompt = e;

  // Show custom banner/notification
  const installBanner = document.createElement("div");
  installBanner.innerHTML = `
    <div id="pwa-install-banner" style="
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: #121821;
      color: #fff;
      padding: 15px 20px;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      display: flex;
      align-items: center;
      gap: 10px;
      z-index: 9999;
    ">
      <span>📲 Install GlobeMTV for faster access!</span>
      <button id="install-btn" style="
        background: #5b8cff;
        color: #fff;
        border: none;
        padding: 8px 14px;
        border-radius: 8px;
        cursor: pointer;
      ">Install</button>
      <button id="close-btn" style="
        background: transparent;
        color: #aaa;
        border: none;
        font-size: 18px;
        cursor: pointer;
      ">✕</button>
    </div>
  `;
  document.body.appendChild(installBanner);

  // Handle Install button
  document.getElementById("install-btn").addEventListener("click", async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      console.log("User response:", outcome);
      deferredPrompt = null;
      document.getElementById("pwa-install-banner").remove();
    }
  });

  // Handle Close button
  document.getElementById("close-btn").addEventListener("click", () => {
    document.getElementById("pwa-install-banner").remove();
  });
});
