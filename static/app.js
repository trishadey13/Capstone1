const SPOON_API = "https://api.spoonacular.com"
const API_KEY = "3630282f6c42420fa7099731b3f21509"

async function seeNutrition() {
    const nutritionModal = document.getElementsByClassName("modal")[0];
    const nutritionInfo = document.getElementsByClassName("nutritionInfoHere")[0];

    const recipeId = window.event.target.classList[1];
    const recipeNutrition = await axios.get(`${SPOON_API}/recipes/${recipeId}/nutritionWidget?apiKey=${API_KEY}&defaultCss=true`);
    
    $('.nutritionInfoHere').append(recipeNutrition.data);
    nutritionModal.style.display = "block";

    // close modal if X is clicked
    $(".close").on("click", function (evt) {
        nutritionModal.style.display = "none";
        nutritionInfo.innerHTML = '';
    })

    // close modal if clicked outside of modal
    window.onclick = function(evt) {
        if (evt.target == nutritionModal) {
            nutritionModal.style.display = "none";
            nutritionInfo.innerHTML = '';
        }
    }
}

$('.heart').on('click', async function(evt) {
    evt.preventDefault();

    recipeHeart = evt.target;
    recipeId = recipeHeart.parentElement.id;
    liked = true;

    if (recipeHeart.classList.contains('far')) {   
        recipeHeart.classList.remove('far'); //not liked
        recipeHeart.classList.add('fas'); //like
    } else {
        liked = false;
        recipeHeart.classList.remove('fas'); //liked
        recipeHeart.classList.add('far'); //not like
    }
    
    const response = await axios.post('/like', {
        body: {
            recipeId: recipeId,
            liked: liked
          }
    });
    
})