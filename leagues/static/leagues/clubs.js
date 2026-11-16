
const clubForm = document.querySelector(".club-form");
const ClubName = document.querySelector("#clubname");
const cityName = document.querySelector("#city");
const errorplace = document.querySelector("#ErrorPlace");

if (clubForm && ClubName && cityName && errorplace) {
    clubForm.addEventListener("submit", (e) => {
        if (!ClubName.value.trim()) {
            e.preventDefault();
            errorplace.innerText = "نام باشگاه را وارد کن!";
        } else {
            errorplace.innerText = "";
        }
    });
}
