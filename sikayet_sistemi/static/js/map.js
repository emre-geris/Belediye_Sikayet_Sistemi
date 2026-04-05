// Initialize map and add complaint markers
function initializeComplaintMap(complaints) {
   // Istanbul center coordinates
   const ISTANBUL_CENTER = [41.0082, 28.9784];
   const DEFAULT_ZOOM = 11;

   // Create map
   const map = L.map("complaint-map").setView(ISTANBUL_CENTER, DEFAULT_ZOOM);

   // Add Esri World Street Map tile layer (no referer issues)
   L.tileLayer(
      "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
      {
         attribution: "Tiles &copy; Esri",
         maxZoom: 19,
      },
   ).addTo(map);

   // Ensure complaints is an array
   if (!complaints || !Array.isArray(complaints)) {
      console.warn("No complaints data provided or invalid format");
      return;
   }

   // Add markers for each complaint with coordinates
   complaints.forEach((complaint) => {
      if (complaint.latitude && complaint.longitude) {
         const marker = L.marker([complaint.latitude, complaint.longitude], {
            title: complaint.title,
         }).addTo(map);

         // Create popup content
         const popupContent = `
                    <div class="leaflet-popup-content" style="width: 250px;">
                        <div style="margin-bottom: 10px;">
                            <strong style="color: #40513b; font-size: 14px;">${escapeHtml(complaint.title)}</strong>
                        </div>
                        <div style="margin-bottom: 8px; font-size: 12px; color: #5e6b5a;">
                            <strong>İlçe:</strong> ${escapeHtml(complaint.district || "Bilinmiyor")}
                        </div>
                        <div style="margin-bottom: 8px; font-size: 12px; color: #5e6b5a;">
                            <strong>Kategori:</strong> ${getCategoryLabel(complaint.category)}
                        </div>
                        <div style="margin-bottom: 8px; font-size: 12px; color: #5e6b5a;">
                            <strong>Öncelik:</strong> <span style="color: ${getPriorityColor(complaint.priority)}">${getPriorityLabel(complaint.priority)}</span>
                        </div>
                        <div style="margin-bottom: 10px; font-size: 12px; color: #5e6b5a; line-height: 1.4;">
                            ${escapeHtml(complaint.description.substring(0, 100))}${complaint.description.length > 100 ? "..." : ""}
                        </div>
                        <a href="/sikayet/${complaint.id}/" style="
                            display: inline-block;
                            background-color: #40513b;
                            color: white;
                            padding: 6px 12px;
                            border-radius: 4px;
                            text-decoration: none;
                            font-size: 12px;
                            font-weight: bold;
                        ">Detayları Gör →</a>
                    </div>
                `;

         marker.bindPopup(popupContent);
      }
   });

   // Fit map to bounds if we have multiple markers
   if (complaints && complaints.length > 0) {
      const markers = document.querySelectorAll(".leaflet-marker-icon");
      if (markers.length > 1) {
         const group = new L.featureGroup(map._layers);
         map.fitBounds(group.getBounds().pad(0.1));
      }
   }
}

// Helper function to escape HTML special characters
function escapeHtml(text) {
   const div = document.createElement("div");
   div.textContent = text;
   return div.innerHTML;
}

// Helper function to get category label in Turkish
function getCategoryLabel(category) {
   const categoryLabels = {
      infrastructure: "Altyapı",
      traffic: "Trafik",
      pothole: "Çukur",
      water: "Su Kaçağı",
      trash: "Çöp",
      other: "Diğer",
   };
   return categoryLabels[category] || category;
}

// Helper function to get priority label in Turkish
function getPriorityLabel(priority) {
   const priorityLabels = {
      low: "Düşük",
      medium: "Orta",
      high: "Yüksek",
      urgent: "Acil",
   };
   return priorityLabels[priority] || priority;
}

// Helper function to get priority color
function getPriorityColor(priority) {
   const priorityColors = {
      low: "#10b981",
      medium: "#f59e0b",
      high: "#ef4444",
      urgent: "#991b1b",
   };
   return priorityColors[priority] || "#40513b";
}

// Initialize map when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
   const mapContainer = document.getElementById("complaint-map");
   if (mapContainer) {
      // Read complaints data from data attribute
      const complaintsDataStr = mapContainer.getAttribute("data-complaints");
      let complaints = [];

      if (complaintsDataStr) {
         try {
            complaints = JSON.parse(complaintsDataStr);
            console.log("Loaded complaints data:", complaints);
         } catch (e) {
            console.error("Error parsing complaints data:", e);
         }
      }

      initializeComplaintMap(complaints);
   }
});
