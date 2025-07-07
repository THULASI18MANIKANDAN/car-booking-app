// Flash message auto-hide
document.addEventListener("DOMContentLoaded", () => {
  const flashMessages = document.querySelectorAll(".flash-message")

  flashMessages.forEach((message) => {
    setTimeout(() => {
      message.style.opacity = "0"
      message.style.transform = "translateX(100%)"
      setTimeout(() => {
        message.remove()
      }, 300)
    }, 5000)
  })
})

// Mobile navigation toggle
function toggleMobileNav() {
  const navMenu = document.querySelector(".nav-menu")
  navMenu.classList.toggle("active")
}

// Form validation
function validateForm(formId) {
  const form = document.getElementById(formId)
  const inputs = form.querySelectorAll("input[required], select[required], textarea[required]")
  let isValid = true

  inputs.forEach((input) => {
    if (!input.value.trim()) {
      input.classList.add("error")
      isValid = false
    } else {
      input.classList.remove("error")
    }
  })

  return isValid
}

// Date validation for booking form
function validateBookingDates() {
  const startDate = document.getElementById("start_date")
  const endDate = document.getElementById("end_date")

  if (startDate && endDate) {
    const start = new Date(startDate.value)
    const end = new Date(endDate.value)
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    if (start < today) {
      alert("Start date cannot be in the past")
      return false
    }

    if (end < start) {
      alert("End date cannot be before start date")
      return false
    }
  }

  return true
}

// Smooth scrolling for anchor links
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

// Loading state for buttons
function showLoading(button) {
  const originalText = button.innerHTML
  button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...'
  button.disabled = true

  return () => {
    button.innerHTML = originalText
    button.disabled = false
  }
}

// Confirmation dialogs
function confirmAction(message) {
  return confirm(message)
}

// Auto-resize textareas
document.addEventListener("DOMContentLoaded", () => {
  const textareas = document.querySelectorAll("textarea")

  textareas.forEach((textarea) => {
    textarea.addEventListener("input", function () {
      this.style.height = "auto"
      this.style.height = this.scrollHeight + "px"
    })
  })
})

// Image preview for file uploads
function previewImage(input, previewId) {
  if (input.files && input.files[0]) {
    const reader = new FileReader()

    reader.onload = (e) => {
      const preview = document.getElementById(previewId)
      if (preview) {
        preview.src = e.target.result
        preview.style.display = "block"
      }
    }

    reader.readAsDataURL(input.files[0])
  }
}

// Search functionality
function searchTable(inputId, tableId) {
  const input = document.getElementById(inputId)
  const table = document.getElementById(tableId)

  if (input && table) {
    input.addEventListener("keyup", function () {
      const filter = this.value.toLowerCase()
      const rows = table.getElementsByTagName("tr")

      for (let i = 1; i < rows.length; i++) {
        const row = rows[i]
        const cells = row.getElementsByTagName("td")
        let found = false

        for (let j = 0; j < cells.length; j++) {
          if (cells[j].textContent.toLowerCase().indexOf(filter) > -1) {
            found = true
            break
          }
        }

        row.style.display = found ? "" : "none"
      }
    })
  }
}

// Copy to clipboard
function copyToClipboard(text) {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      showToast("Copied to clipboard!", "success")
    })
    .catch(() => {
      // Fallback for older browsers
      const textArea = document.createElement("textarea")
      textArea.value = text
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand("copy")
      document.body.removeChild(textArea)
      showToast("Copied to clipboard!", "success")
    })
}

// Show toast notification
function showToast(message, type = "info") {
  const toast = document.createElement("div")
  toast.className = `flash-message flash-${type}`
  toast.innerHTML = `
        <i class="fas fa-${type === "success" ? "check-circle" : type === "error" ? "exclamation-circle" : "info-circle"}"></i>
        ${message}
        <button class="flash-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `

  const container = document.querySelector(".flash-messages") || createFlashContainer()
  container.appendChild(toast)

  setTimeout(() => {
    toast.style.opacity = "0"
    toast.style.transform = "translateX(100%)"
    setTimeout(() => toast.remove(), 300)
  }, 5000)
}

function createFlashContainer() {
  const container = document.createElement("div")
  container.className = "flash-messages"
  document.body.appendChild(container)
  return container
}

// Initialize tooltips
function initTooltips() {
  const tooltips = document.querySelectorAll("[data-tooltip]")

  tooltips.forEach((element) => {
    element.addEventListener("mouseenter", function () {
      const tooltip = document.createElement("div")
      tooltip.className = "tooltip"
      tooltip.textContent = this.getAttribute("data-tooltip")
      document.body.appendChild(tooltip)

      const rect = this.getBoundingClientRect()
      tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + "px"
      tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + "px"
    })

    element.addEventListener("mouseleave", () => {
      const tooltip = document.querySelector(".tooltip")
      if (tooltip) {
        tooltip.remove()
      }
    })
  })
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  initTooltips()

  // Add loading states to forms
  const forms = document.querySelectorAll("form")
  forms.forEach((form) => {
    form.addEventListener("submit", () => {
      const submitButton = form.querySelector('button[type="submit"]')
      if (submitButton) {
        showLoading(submitButton)
      }
    })
  })
})
