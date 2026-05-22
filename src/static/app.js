console.log("app.js loaded");

document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const messageDiv = document.getElementById("message");
  const searchInput = document.getElementById("search-input");
  const categoryFilter = document.getElementById("category-filter");
  const sortFilter = document.getElementById("sort-filter");
  const loginBtn = document.getElementById("login-btn");

  let isAdmin = false;

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      let filteredActivities = Object.entries(activities);

      const searchValue = searchInput.value.toLowerCase();
      const categoryValue = categoryFilter.value;
      const sortValue = sortFilter.value;

      filteredActivities = filteredActivities.filter(([name, details]) => {
        const matchesSearch =
          name.toLowerCase().includes(searchValue) ||
          details.description.toLowerCase().includes(searchValue);

        const matchesCategory =
          categoryValue === "all" ||
          details.category?.toLowerCase() === categoryValue;

        return matchesSearch && matchesCategory;
      });

      if (sortValue === "name") {
        filteredActivities.sort((a, b) => a[0].localeCompare(b[0]));
      } else if (sortValue === "spots") {
        filteredActivities.sort((a, b) => {
          const spotsA =
            a[1].max_participants - a[1].participants.length;

          const spotsB =
            b[1].max_participants - b[1].participants.length;

          return spotsB - spotsA;
        });
      }
      filteredActivities.forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft =
          details.max_participants - details.participants.length;

        // Create participants HTML with delete icons instead of bullet points
        const participantsHTML =
          details.participants.length > 0
            ? `<div class="participants-section">
              <h5>Participants:</h5>
              <ul class="participants-list">
                ${details.participants
                  .map(
                    (email) =>
                      `<li><span class="participant-email">${email}</span><button class="delete-btn" data-activity="${name}" data-email="${email}">❌</button></li>`
                  )
                  .join("")}
              </ul>
            </div>`
            : `<p><em>No participants yet</em></p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <button class="register-btn" data-activity="${name}">
            Register Student
          </button>
          <div class="participants-container">
            ${participantsHTML}
          </div>
        `;

        activitiesList.appendChild(activityCard);
      });
      // Add event listeners to register buttons
      document.querySelectorAll(".register-btn").forEach((button) => {
        button.addEventListener("click", async () => {
          const email = prompt("Enter student email:");
          if (!email) return;

          const activity = button.getAttribute("data-activity");

          try {
            const response = await fetch(
              `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}&admin=${isAdmin}`,
              {
                method: "POST",
              }
            );

            const result = await response.json();

            if (response.ok) {
              messageDiv.textContent = result.message;
              messageDiv.className = "success";
              fetchActivities();
            } else {
              messageDiv.textContent = result.detail || "An error occurred";
              messageDiv.className = "error";
            }

            messageDiv.classList.remove("hidden");

            setTimeout(() => {
              messageDiv.classList.add("hidden");
            }, 5000);

          } catch (error) {
            messageDiv.textContent = "Failed to sign up. Please try again.";
            messageDiv.className = "error";
            messageDiv.classList.remove("hidden");
            console.error("Error signing up:", error);
          }
        });
      });
      // Add event listeners to delete buttons
      document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", handleUnregister);
      });
    } catch (error) {
      activitiesList.innerHTML =
        "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle unregister functionality
  async function handleUnregister(event) {
    const button = event.target;
    const activity = button.getAttribute("data-activity");
    const email = button.getAttribute("data-email");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/unregister?email=${encodeURIComponent(email)}&admin=${isAdmin}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";

        // Refresh activities list to show updated participants
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to unregister. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error unregistering:", error);
    }
  }

  loginBtn.addEventListener("click", async () => {
    const username = prompt("Enter teacher username:");
    const password = prompt("Enter teacher password:");

    if (!username || !password) return;

    try {
      const response = await fetch(
        `/login?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        isAdmin = true;
        alert("Teacher login successful");
      } else {
        alert(result.detail || "Login failed");
      }
    } catch (error) {
      alert("Login request failed");
    }
  });
  searchInput.addEventListener("input", fetchActivities);

  categoryFilter.addEventListener("change", fetchActivities);

  sortFilter.addEventListener("change", fetchActivities);
  // Initialize app
  fetchActivities();
});
