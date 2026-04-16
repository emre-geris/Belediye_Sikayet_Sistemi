// Istanbul Districts and their coordinates
const ISTANBUL_DISTRICTS = {
   Adalar: [40.8795, 29.1261],
   Avcılar: [41.0361, 28.7531],
   Bahçelievler: [41.0208, 28.8908],
   Bakırköy: [41.0264, 28.9092],
   Başakşehir: [41.1789, 28.8147],
   Bayrampasa: [41.0433, 28.9064],
   Beşiktaş: [41.0758, 29.0019],
   Beykoz: [41.2309, 29.1228],
   Beyoğlu: [41.0456, 28.9739],
   "Böcek Köy": [41.3178, 29.2628],
   Büyükçekmece: [41.0414, 28.5929],
   Çatalca: [41.1844, 28.4506],
   Çekmeköy: [41.1972, 29.3222],
   Esenler: [41.0308, 28.8928],
   Esenyurt: [41.0553, 28.7256],
   Eyüp: [41.0556, 28.9244],
   Eyüpsultan: [41.0556, 28.9244],
   Gaziosmanpaşa: [41.0958, 28.8839],
   Güngören: [41.0136, 28.9064],
   Kadıköy: [40.9891, 29.0289],
   Kağıthane: [41.0836, 28.9756],
   Kartal: [40.9072, 29.2775],
   Kasımpaşa: [41.0542, 28.9722],
   Küçükçekmece: [41.0172, 28.7639],
   Küçükyalı: [40.9769, 29.0694],
   Levent: [41.0828, 29.0236],
   Maslak: [41.1056, 29.0103],
   Maltepe: [40.9647, 29.1364],
   Pendik: [40.8931, 29.2489],
   Sarıyer: [41.1497, 29.0961],
   Şile: [41.1608, 29.62],
   Şişli: [41.0873, 28.9883],
   Taksim: [41.0369, 28.9855],
   Tuzla: [40.8419, 29.305],
   Ümraniye: [41.0325, 29.1122],
   Üsküdar: [41.0096, 29.0276],
   Zeytinburnu: [40.9928, 28.8906],
};

document.addEventListener("DOMContentLoaded", function () {
   const districtSelect = document.getElementById("district-select");
   const latitudeField = document.getElementById("id_latitude");
   const longitudeField = document.getElementById("id_longitude");

   if (districtSelect && latitudeField && longitudeField) {
      // Set coordinates when district is selected
      districtSelect.addEventListener("change", function () {
         const selectedDistrict = this.value;
         if (selectedDistrict && ISTANBUL_DISTRICTS[selectedDistrict]) {
            const [lat, lon] = ISTANBUL_DISTRICTS[selectedDistrict];
            latitudeField.value = lat;
            longitudeField.value = lon;
         } else {
            latitudeField.value = "";
            longitudeField.value = "";
         }
      });
   }
});
