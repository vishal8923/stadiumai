const fs = require('fs');
const path = require('path');

const dataDir = path.join(__dirname, 'app', 'data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

// 1. FAQ (50 entries)
const faq = [];
for (let i = 1; i <= 50; i++) {
  faq.push({
    id: `faq_${i}`,
    question: `What is the policy on bag size at the stadium? Question ${i}`,
    answer: `Small bags, purses, and clutches are allowed if they do not exceed 12x6x12 inches. Clear bags are highly recommended for fast processing. Item ${i} reference.`,
    keywords: ["bag", "size", "clear", "purse", "allowed", "prohibited", `item_${i}`]
  });
}
// Add some specific FIFA/Stadium FAQs
faq[0] = {
  id: "faq_bag_policy",
  question: "What is the bag policy for the stadium?",
  answer: "Bags must be clear plastic, vinyl, or PVC and not exceed 12\" x 6\" x 12\". Small clutch bags, approximately the size of a hand, are allowed.",
  keywords: ["bag", "size", "backpack", "clutch", "purse", "prohibited"]
};
faq[1] = {
  id: "faq_reentry",
  question: "Am I allowed to leave the stadium and re-enter?",
  answer: "Re-entry is strictly prohibited at FIFA World Cup 2026 matches. Once you scan your ticket and exit the gates, you cannot return.",
  keywords: ["re-entry", "leave", "exit", "return", "ticket", "in and out"]
};
faq[2] = {
  id: "faq_prohibited_items",
  question: "What items are prohibited inside the stadium?",
  answer: "Prohibited items include weapons, professional cameras, drones, large banners, laser pointers, bottles, cans, and outside food or beverages.",
  keywords: ["prohibited", "weapons", "cameras", "drones", "food", "bottles", "cans", "alcohol"]
};
faq[3] = {
  id: "faq_gates_open",
  question: "What time do the stadium gates open before kickoff?",
  answer: "Gates open exactly 3 hours prior to kickoff. We strongly recommend arriving early to clear security and enjoy pre-match fan zone entertainment.",
  keywords: ["gates", "open", "kickoff", "time", "arrival", "early"]
};
faq[4] = {
  id: "faq_wi_fi",
  question: "Is there free Wi-Fi available at the stadium?",
  answer: "Yes, connect to the SSID '#FIFAWorldCup2026-FreeWiFi' throughout the concourses and seating bowl. No password is required.",
  keywords: ["wifi", "internet", "connection", "free", "network", "ssids"]
};

// 2. Policies (30 entries)
const policies = [];
for (let i = 1; i <= 30; i++) {
  policies.push({
    id: `policy_${i}`,
    policy: `Stadium Conduct Guideline ${i}`,
    description: `Guests must behave respectfully. Inappropriate language or gestures are prohibited. Compliance with policy ${i} is mandatory.`,
    keywords: ["conduct", "behavior", "rules", `policy_${i}`]
  });
}
policies[0] = {
  id: "policy_smoking",
  policy: "Smoking and Vaping Policy",
  description: "The stadium is a 100% smoke-free and vape-free facility. Designated smoking areas are not available inside the security perimeter.",
  keywords: ["smoking", "vaping", "vape", "cigar", "tobacco", "smoke"]
};
policies[1] = {
  id: "policy_alcohol",
  policy: "Alcohol Sales and Consumption Policy",
  description: "Alcohol (beer and wine) is sold to guests aged 21 and over with valid ID. Sales cut off at the 75th minute of the match. Limit 2 drinks per purchase.",
  keywords: ["alcohol", "beer", "wine", "drinking", "id", "age", "75th minute"]
};
policies[2] = {
  id: "policy_code_of_conduct",
  policy: "Fan Code of Conduct",
  description: "Fans are expected to support their teams positively. Harassment, fighting, throwing objects, or pitch invasion will result in immediate ejection and arrest.",
  keywords: ["conduct", "harassment", "fighting", "pitch", "arrest", "ejection"]
};

// 3. Food Menus (20 entries)
const foodMenus = [];
for (let i = 1; i <= 20; i++) {
  foodMenus.push({
    id: `menu_${i}`,
    name: `Food Court Vendor ${i}`,
    location: i % 2 === 0 ? "Concourse North" : "Concourse South",
    menu: [
      { item: `World Cup Burger ${i}`, price: 12.99, tags: ["halal", "meat"] },
      { item: `FIFA Fries ${i}`, price: 5.99, tags: ["vegetarian", "vegan"] },
      { item: `Soft Drink ${i}`, price: 4.50, tags: ["beverage", "cold"] }
    ]
  });
}
foodMenus[0] = {
  id: "menu_north_court",
  name: "Food Court North",
  location: "Concourse 1 (Level 1)",
  menu: [
    { item: "Classic Cheeseburger", price: 11.50, tags: ["meat", "popular"] },
    { item: "Halal Chicken Shawarma", price: 13.00, tags: ["halal", "poultry"] },
    { item: "Vegan Falafel Wrap", price: 10.50, tags: ["vegan", "vegetarian", "gluten-free"] },
    { item: "Salted Soft Pretzel", price: 6.00, tags: ["vegetarian"] },
    { item: "Coca-Cola / Sprite", price: 5.00, tags: ["beverage"] }
  ]
};
foodMenus[1] = {
  id: "menu_south_court",
  name: "Food Court South",
  location: "Concourse 3 (Level 1)",
  menu: [
    { item: "Pepperoni Pizza Slice", price: 8.50, tags: ["meat"] },
    { item: "Margherita Pizza Slice", price: 7.50, tags: ["vegetarian"] },
    { item: "Tacos Al Pastor (3x)", price: 12.00, tags: ["meat", "gluten-free"] },
    { item: "Nachos with Warm Cheese", price: 7.00, tags: ["vegetarian"] },
    { item: "Local Craft Beer", price: 12.50, tags: ["alcohol", "beverage"] }
  ]
};

// 4. Transport (15 entries)
const transport = [];
for (let i = 1; i <= 15; i++) {
  transport.push({
    id: `transport_${i}`,
    mode: i % 3 === 0 ? "Bus" : (i % 3 === 1 ? "Metro" : "Shuttle"),
    route: `Route ${i + 100}`,
    destination: `Destination Zone ${i}`,
    schedule_details: `Runs every ${5 + i} minutes during match days.`,
    keywords: ["transport", "commute", "shuttle", "bus", "metro", `route_${i}`]
  });
}
transport[0] = {
  id: "trans_metro_red",
  mode: "Metro",
  route: "Red Line (Stadium Station)",
  destination: "Downtown / City Center",
  schedule_details: "Runs every 3 minutes post-match. Accessible ramps at all platforms.",
  keywords: ["metro", "train", "subway", "red line", "downtown", "city center", "station"]
};
transport[1] = {
  id: "trans_shuttle_parking",
  mode: "Shuttle",
  route: "Lot B Express Shuttle",
  destination: "Parking Lot B / West Gate",
  schedule_details: "Continuous service starting 4 hours pre-match to 2 hours post-match.",
  keywords: ["shuttle", "bus", "parking", "lot b", "express", "ride"]
};

// 5. Emergency (20 entries)
const emergency = [];
for (let i = 1; i <= 20; i++) {
  emergency.push({
    id: `emergency_${i}`,
    scenario: `Incidental Event Protocol ${i}`,
    protocol: `Evacuate via nearest signed exit ${i}. Follow coordinator directives.`,
    assembly_point: `Assembly Yard ${String.fromCharCode(65 + (i % 4))}`,
    keywords: ["emergency", "fire", "exit", `protocol_${i}`]
  });
}
emergency[0] = {
  id: "em_medical_emergency",
  scenario: "Medical Emergency or Injury",
  protocol: "Locate nearest staff member or dial the in-stadium emergency line at 911-STAD. Stay with the patient and do not block concourse flow.",
  assembly_point: "Nearest Medical Room (Station 1 near Gate C, Station 2 near Gate G)",
  keywords: ["medical", "injury", "bleeding", "hurt", "heart", "unconscious", "ambulance", "doctor", "emergency"]
};
emergency[1] = {
  id: "em_fire_alarm",
  scenario: "Fire Alarm and Evacuation",
  protocol: "If a fire alarm sounds, proceed calmly to the nearest exit gate (Gates A-H). Do not use elevators. Assist those with mobility challenges.",
  assembly_point: "External Assembly Plaza North/South",
  keywords: ["fire", "smoke", "burning", "evacuate", "alarm", "exit", "stairwell"]
};

// 6. Accessibility (15 entries)
const accessibility = [];
for (let i = 1; i <= 15; i++) {
  accessibility.push({
    id: `access_${i}`,
    service_type: i % 2 === 0 ? "elevator" : "ramp",
    location: `Concourse Level ${i % 4 + 1}`,
    details: `Standard accessibility assistance unit ${i}. Open for public utilization.`,
    keywords: ["accessible", "wheelchair", "elevator", "ramp", `unit_${i}`]
  });
}
accessibility[0] = {
  id: "access_elevators",
  service_type: "elevator",
  location: "Elevators 1-6 near concourses",
  details: "Six high-capacity passenger elevators are available to transfer patrons between Levels 1, 2, 3, and 4. Staff are on duty to assist.",
  keywords: ["elevator", "lift", "wheelchair", "stairs", "levels", "accessible"]
};
accessibility[1] = {
  id: "access_restrooms",
  service_type: "restroom",
  location: "Sections 4, 12, 20, 28",
  details: "All washrooms contain accessible stalls with grab bars. Family/unisex companion restrooms are located next to Main restrooms.",
  keywords: ["restroom", "toilet", "washroom", "accessible", "wheelchair", "grab bar"]
};

// Write files
fs.writeFileSync(path.join(dataDir, 'faq.json'), JSON.stringify(faq, null, 2));
fs.writeFileSync(path.join(dataDir, 'policies.json'), JSON.stringify(policies, null, 2));
fs.writeFileSync(path.join(dataDir, 'food_menus.json'), JSON.stringify(foodMenus, null, 2));
fs.writeFileSync(path.join(dataDir, 'transport.json'), JSON.stringify(transport, null, 2));
fs.writeFileSync(path.join(dataDir, 'emergency.json'), JSON.stringify(emergency, null, 2));
fs.writeFileSync(path.join(dataDir, 'accessibility.json'), JSON.stringify(accessibility, null, 2));

console.log("Successfully generated all mock RAG JSON data files!");
