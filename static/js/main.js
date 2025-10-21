// Form submission for crop recommendations
document.getElementById('farm-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Get form values
    const landSize = document.getElementById('land-size').value;
    const soilType = document.getElementById('soil-type').value;
    const location = document.getElementById('location').value;
    const fertilizer = document.getElementById('fertilizer').value;
    const waterAccess = document.getElementById('water-access').value;
    
    // In a real application, this would be processed by a backend with ML algorithms
    // For this demo, we'll use simple logic based on the inputs
    
    let recommendations = [];
    
    // Basic recommendation logic (simplified for demo)
    if (soilType === 'loamy' && parseFloat(landSize) >= 5) {
        recommendations.push({name: 'Maize', icon: '🌽', suitability: 'High'});
        recommendations.push({name: 'Beans', icon: '🫘', suitability: 'High'});
    }
    
    if (soilType === 'clay' || waterAccess === 'irrigation') {
        recommendations.push({name: 'Rice', icon: '🌾', suitability: 'Medium'});
    }
    
    if (fertilizer === 'organic' && parseFloat(landSize) < 5) {
        recommendations.push({name: 'Vegetables', icon: '🥬', suitability: 'High'});
    }
    
    if (soilType === 'sandy' && waterAccess === 'irrigation') {
        recommendations.push({name: 'Groundnuts', icon: '🥜', suitability: 'Medium'});
    }
    
    // Fallback recommendations if none matched
    if (recommendations.length === 0) {
        recommendations.push({name: 'Maize', icon: '🌽', suitability: 'Medium'});
        recommendations.push({name: 'Beans', icon: '🫘', suitability: 'Medium'});
    }
    
    // Display recommendations
    const resultsDiv = document.getElementById('recommendation-results');
    let html = `<div class="recommendation">
                    <h3>Recommended Crops for Your Farm</h3>
                    <p>Based on your inputs: ${landSize} acres, ${soilType} soil in ${location}</p>
                    <div class="grid-3" style="margin-top: 20px;">`;
    
    recommendations.forEach(crop => {
        html += `<div class="crop-card">
                    <div class="crop-icon">${crop.icon}</div>
                    <h4>${crop.name}</h4>
                    <p>Suitability: ${crop.suitability}</p>
                 </div>`;
    });
    
    html += `</div></div>`;
    resultsDiv.innerHTML = html;
});


// Simulate weather data
document.addEventListener('DOMContentLoaded', function() {
    const forecastDiv = document.getElementById('weather-forecast');
    const days = ['Today', 'Tomorrow', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const icons = ['☀️', '⛅', '🌧️', '⛅', '☀️', '☀️', '🌧️'];
    const temps = ['28°C', '27°C', '25°C', '26°C', '29°C', '30°C', '26°C'];
    
    let html = '';
    for (let i = 0; i < days.length; i++) {
        html += `<div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee;">
                    <span>${days[i]}</span>
                    <span>${icons[i]}</span>
                    <span>${temps[i]}</span>
                 </div>`;
    }
    forecastDiv.innerHTML = html;
});

// Blog post submission
document.getElementById('blog-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const content = document.getElementById('blog-content').value;
    
    if (content.trim() === '') return;
    
    const blogPostsDiv = document.getElementById('blog-posts');
    const timeString = 'Just now';
    
    const newPost = document.createElement('div');
    newPost.className = 'blog-post';
    newPost.innerHTML = `
        <div class="blog-meta">
            <span><i class="fas fa-user"></i> You</span>
            <span><i class="far fa-clock"></i> ${timeString}</span>
        </div>
        <p>${content}</p>
    `;
    
    blogPostsDiv.prepend(newPost);
    document.getElementById('blog-content').value = '';
});