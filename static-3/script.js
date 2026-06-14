document.addEventListener("DOMContentLoaded", function() {
    const activityText = document.getElementById("activity-text");
    const activityType = document.getElementById("activity-type");
    const activityParticipants = document.getElementById("activity-participants");
    const activityPrice = document.getElementById("activity-price");
    const newActivityBtn = document.getElementById("newActivityBtn");
    const saveActivityBtn = document.getElementById("saveActivityBtn");

    function showError(message) {
        alert(message);
    }

    newActivityBtn.addEventListener("click", function() {
        $.ajax({
            url: "/get_new_activity",
            method: "GET",
            dataType: "json",
            success: function(data) {
                activityText.textContent = data.activity;
                activityType.textContent = data.type;
                activityParticipants.textContent = data.participants;
                activityPrice.textContent = data.price;
            },
            error: function(xhr, status, error) {
                console.error("Napaka:", error);
                showError("Napaka pri nalaganju aktivnosti.");
            }
        });
    });

    saveActivityBtn.addEventListener("click", function() {
        const payload = {
            activity: activityText.textContent,
            type: activityType.textContent,
            participants: activityParticipants.textContent,
            price: activityPrice.textContent
        };

        $.ajax({
            url: "/save_activity",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify(payload),
            dataType: "json",
            success: function(response) {
                if (response.status === "success") {
                    location.reload();   // osvežitev – Jinja ponovno nariše seznam
                } else {
                    showError(response.message);
                }
            },
            error: function(xhr, status, error) {
                let msg = "Napaka pri shranjevanju aktivnosti.";
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    msg = xhr.responseJSON.message;
                }
                showError(msg);
            }
        });
    });

    const favoritesSection = document.querySelector(".favorites-section");
    favoritesSection.addEventListener("click", function(event) {
        const btn = event.target.closest(".delete-btn");
        if (!btn) return;
        const activityId = btn.getAttribute("data-id");
        if (!activityId) return;

        $.ajax({
            url: "/delete_activity",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ id: activityId }),
            dataType: "json",
            success: function(response) {
                if (response.status === "success") {
                    location.reload();
                } else {
                    showError(response.message);
                }
            },
            error: function(xhr, status, error) {
                showError("Napaka pri brisanju aktivnosti.");
            }
        });
    });
});