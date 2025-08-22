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