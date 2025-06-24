// Smooth scrolling para los enlaces del menú
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault()
    const target = document.querySelector(this.getAttribute("href"))
    if (target) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      })
    }
  })
})

// Navbar scroll effect
window.addEventListener("scroll", () => {
  const navbar = document.querySelector(".navbar-custom")
  if (window.scrollY > 100) {
    navbar.style.background = "rgba(255, 255, 255, 0.95)"
    navbar.style.backdropFilter = "blur(10px)"
  } else {
    navbar.style.background = "#ffffff"
    navbar.style.backdropFilter = "none"
  }
})

// Animaciones al hacer scroll
const observerOptions = {
  threshold: 0.1,
  rootMargin: "0px 0px -50px 0px",
}

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = "1"
      entry.target.style.transform = "translateY(0)"
    }
  })
}, observerOptions)

// Aplicar animaciones a las tarjetas de productos
document.querySelectorAll(".producto-card").forEach((card) => {
  card.style.opacity = "0"
  card.style.transform = "translateY(30px)"
  card.style.transition = "opacity 0.6s ease, transform 0.6s ease"
  observer.observe(card)
})

// Aplicar animaciones a las tarjetas del dashboard
document.querySelectorAll(".dashboard-card").forEach((card) => {
  card.style.opacity = "0"
  card.style.transform = "translateY(20px)"
  card.style.transition = "opacity 0.5s ease, transform 0.5s ease"
  observer.observe(card)
})

// Auto-dismiss alerts después de 5 segundos
document.querySelectorAll(".alert").forEach((alert) => {
  setTimeout(() => {
    const bsAlert = window.bootstrap.Alert.getOrCreateInstance(alert)
    bsAlert.close()
  }, 5000)
})

// Validación del formulario de login
const loginForm = document.querySelector(".login-form")
if (loginForm) {
  loginForm.addEventListener("submit", (e) => {
    const username = document.getElementById("username").value
    const password = document.getElementById("password").value

    if (!username || !password) {
      e.preventDefault()
      alert("Por favor, completa todos los campos")
    }
  })
}

// Efecto de typing para el título principal
function typeWriter(element, text, speed = 100) {
  let i = 0
  element.innerHTML = ""

  function type() {
    if (i < text.length) {
      element.innerHTML += text.charAt(i)
      i++
      setTimeout(type, speed)
    }
  }

  type()
}

// Aplicar efecto typing al título principal si existe
const heroTitle = document.querySelector(".hero-title")
if (heroTitle) {
  const originalText = heroTitle.textContent
  setTimeout(() => {
    typeWriter(heroTitle, originalText, 150)
  }, 1000)
}
