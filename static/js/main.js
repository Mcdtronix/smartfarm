// Form submission for crop recommendations
document.getElementById("farm-form").addEventListener("submit", function (e) {
  e.preventDefault();

  // Check if user is authenticated
  const isAuthenticated = document.querySelector(".user-menu") !== null;
  if (!isAuthenticated) {
    alert("Please login to get crop recommendations.");
    window.location.href = "/login/";
    return;
  }

  // Get form values
  const landSize = document.getElementById("land-size").value;
  const soilType = document.getElementById("soil-type").value;
  const location = document.getElementById("location").value;
  const fertilizer = document.getElementById("fertilizer").value;
  const waterAccess = document.getElementById("water-access").value;

  // Show loading state
  const resultsDiv = document.getElementById("recommendation-results");
  resultsDiv.innerHTML =
    '<div class="recommendation"><p><i class="fas fa-spinner fa-spin"></i> Analyzing your farm data and generating recommendations...</p></div>';

  // Prepare data for API call
  const formData = {
    land_size: parseFloat(landSize),
    soil_type: soilType,
    location: location,
    fertilizer_type: fertilizer,
    water_access: waterAccess,
  };

  // Make API call to Django backend
  fetch("/api/crop-recommendations/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify(formData),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        displayRecommendations(data.recommendations, formData);
      } else {
        resultsDiv.innerHTML = `<div class="recommendation" style="background: #ffebee; border-left-color: #f44336;">
                <h3>Error</h3>
                <p>${data.error}</p>
            </div>`;
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      resultsDiv.innerHTML = `<div class="recommendation" style="background: #ffebee; border-left-color: #f44336;">
            <h3>Error</h3>
            <p>Failed to get recommendations. Please try again.</p>
        </div>`;
    });
});

// Function to display recommendations
function displayRecommendations(recommendations, formData) {
  const resultsDiv = document.getElementById("recommendation-results");

  // Crop icons mapping
  const cropIcons = {
    Maize: "🌽",
    Rice: "🌾",
    Wheat: "🌾",
    Barley: "🌾",
    Sorghum: "🌾",
    Millet: "🌾",
    Beans: "🫘",
    Groundnuts: "🥜",
    Soybeans: "🫘",
    Potatoes: "🥔",
    "Sweet Potatoes": "🍠",
    Cassava: "🥔",
    Tomatoes: "🍅",
    Onions: "🧅",
    Cabbage: "🥬",
    Carrots: "🥕",
    Spinach: "🥬",
    Lettuce: "🥬",
    Peppers: "🌶️",
    Eggplant: "🍆",
    Cucumber: "🥒",
    Pumpkin: "🎃",
    Watermelon: "🍉",
    Banana: "🍌",
    Mango: "🥭",
    Avocado: "🥑",
    Coffee: "☕",
    Tea: "🍵",
    Sugarcane: "🎋",
    Cotton: "🌿",
  };

  let html = `<div class="recommendation">
                    <h3>AI-Powered Crop Recommendations</h3>
                    <p>Based on your farm: ${formData.land_size} acres, ${formData.soil_type} soil in ${formData.location}</p>
                    <div class="grid-3" style="margin-top: 20px;">`;

  recommendations.forEach((crop) => {
    const icon = cropIcons[crop.crop_name] || "🌱";
    const scorePercent = Math.round(crop.suitability_score * 100);
    const confidenceColor =
      crop.confidence_level === "high"
        ? "#4caf50"
        : crop.confidence_level === "medium"
        ? "#ff9800"
        : "#f44336";

    html += `<div class="crop-card">
                    <div class="crop-icon">${icon}</div>
                    <h4>${crop.crop_name}</h4>
                    <p>Suitability: ${scorePercent}%</p>
                    <p style="color: ${confidenceColor}; font-weight: bold;">${
      crop.confidence_level.charAt(0).toUpperCase() +
      crop.confidence_level.slice(1)
    } Confidence</p>
                 </div>`;
  });

  html += `</div></div>`;
  resultsDiv.innerHTML = html;
}

// Helper function to get CSRF token
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Load weather data when page loads
document.addEventListener("DOMContentLoaded", function () {
  loadWeatherData();
});

// Weather data loading functions
function loadWeatherData() {
  loadWeatherForecast();
  loadWeatherAlerts();
}

function loadWeatherForecast() {
  const forecastDiv = document.getElementById("weather-forecast");
  if (!forecastDiv) return;

  // Show loading state
  forecastDiv.innerHTML =
    '<p><i class="fas fa-spinner fa-spin"></i> Loading weather forecast...</p>';

  // Get user's location from the farm form or use default
  const locationInput = document.getElementById("location");
  const city = locationInput ? locationInput.value || "Harare" : "Harare";

  fetch(`/api/weather/forecast/?city=${encodeURIComponent(city)}&days=7`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        displayWeatherForecast(data.forecast);
      } else {
        forecastDiv.innerHTML = `<p style="color: #f44336;"><i class="fas fa-exclamation-triangle"></i> ${data.error}</p>`;
      }
    })
    .catch((error) => {
      console.error("Error loading weather forecast:", error);
      forecastDiv.innerHTML =
        '<p style="color: #f44336;"><i class="fas fa-exclamation-triangle"></i> Failed to load weather data</p>';
    });
}

function displayWeatherForecast(forecastData) {
  const forecastDiv = document.getElementById("weather-forecast");
  if (!forecastDiv) return;

  let html = "";
  forecastData.forecast.forEach((day) => {
    const weatherIcon = getWeatherIcon(day.icon);
    html += `
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #eee;">
        <span style="font-weight: 500;">${day.day}</span>
        <span style="font-size: 1.2rem;">${weatherIcon}</span>
        <span style="font-weight: 500;">${day.temperature}°C</span>
      </div>
    `;
  });

  forecastDiv.innerHTML = html;
}

function loadWeatherAlerts() {
  const alertContainer = document.querySelector(".weather-alert");
  if (!alertContainer) return;

  // Get user's location from the farm form or use default
  const locationInput = document.getElementById("location");
  const city = locationInput ? locationInput.value || "Harare" : "Harare";

  fetch(`/api/weather/alerts/?city=${encodeURIComponent(city)}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success && data.alerts.length > 0) {
        displayWeatherAlerts(data.alerts);
      } else {
        // Show default alert if no specific alerts
        alertContainer.innerHTML = `
          <i class="fas fa-info-circle" style="color: var(--primary); font-size: 1.5rem"></i>
          <div>
            <h3>Weather Monitoring Active</h3>
            <p>Weather conditions are being monitored for your area. Check back for updates.</p>
          </div>
        `;
      }
    })
    .catch((error) => {
      console.error("Error loading weather alerts:", error);
      // Keep default alert on error
    });
}

function displayWeatherAlerts(alerts) {
  const alertContainer = document.querySelector(".weather-alert");
  if (!alertContainer || alerts.length === 0) return;

  // Show the first alert (most important)
  const alert = alerts[0];
  const alertIcon = getAlertIcon(alert.type);

  alertContainer.innerHTML = `
    <i class="${alert.icon}" style="color: ${getAlertColor(
    alert.type
  )}; font-size: 1.5rem"></i>
    <div>
      <h3>${alert.title}</h3>
      <p>${alert.message}</p>
    </div>
  `;
}

function getWeatherIcon(iconCode) {
  const iconMap = {
    "01d": "☀️",
    "01n": "🌙",
    "02d": "⛅",
    "02n": "☁️",
    "03d": "☁️",
    "03n": "☁️",
    "04d": "☁️",
    "04n": "☁️",
    "09d": "🌧️",
    "09n": "🌧️",
    "10d": "🌦️",
    "10n": "🌧️",
    "11d": "⛈️",
    "11n": "⛈️",
    "13d": "❄️",
    "13n": "❄️",
    "50d": "🌫️",
    "50n": "🌫️",
  };
  return iconMap[iconCode] || "🌤️";
}

function getAlertIcon(type) {
  const iconMap = {
    warning: "fas fa-exclamation-triangle",
    info: "fas fa-info-circle",
    error: "fas fa-times-circle",
  };
  return iconMap[type] || "fas fa-info-circle";
}

function getAlertColor(type) {
  const colorMap = {
    warning: "var(--secondary)",
    info: "var(--primary)",
    error: "#f44336",
  };
  return colorMap[type] || "var(--primary)";
}

// Blog post submission
document.getElementById("blog-form").addEventListener("submit", function (e) {
  e.preventDefault();
  const content = document.getElementById("blog-content").value;

  if (content.trim() === "") return;

  // Check if user is authenticated
  const isAuthenticated = document.querySelector(".user-menu") !== null;
  if (!isAuthenticated) {
    alert("Please login to post in the community.");
    window.location.href = "/login/";
    return;
  }

  // Show loading state
  const submitBtn = this.querySelector('button[type="submit"]');
  const originalText = submitBtn.textContent;
  submitBtn.textContent = "Posting...";
  submitBtn.disabled = true;

  // Prepare data for API call
  const postData = {
    content: content,
  };

  // Make API call to Django backend
  fetch("/api/community-posts/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify(postData),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Add the new post to the top of the list
        const blogPostsDiv = document.getElementById("blog-posts");
        const newPost = document.createElement("div");
        newPost.className = "blog-post";
        newPost.innerHTML = `
                <div class="blog-meta">
                    <span><i class="fas fa-user"></i> ${data.post.author_name}</span>
                    <span><i class="far fa-clock"></i> ${data.post.created_at}</span>
                </div>
                <p>${data.post.content}</p>
            `;

        blogPostsDiv.prepend(newPost);
        document.getElementById("blog-content").value = "";
      } else {
        alert("Error posting: " + data.error);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("Failed to post. Please try again.");
    })
    .finally(() => {
      // Reset button state
      submitBtn.textContent = originalText;
      submitBtn.disabled = false;
    });
});
