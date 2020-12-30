const BASE_URL = "";
const SPOON_API = "https://api.spoonacular.com"
const API_KEY = "3630282f6c42420fa7099731b3f21509"

getHomePageElem();

async function getHomePageElem () {

    const randomRecipes = await axios.get(`${SPOON_API}/recipes/complexSearch?number=100&apiKey=${API_KEY}`);
    for (let r=0; r<5; r++) {
        randNum = Math.floor(Math.random() * 100) + 1;
        let randRecipeId = randomRecipes.data.results[randNum].id;
        const randRecipe = await axios.get(`${SPOON_API}/recipes/${randRecipeId}/information?apiKey=${API_KEY}`);
        let name = randRecipe.data.title;
        let image = randRecipe.data.image;
        let time = randRecipe.data.readyInMinutes;
        let diets = randRecipe.data.diets;
        let container = "random"
        handleRecipe(name, image, time, diets, container);
    }

    const popularRecipes = await axios.get(`${SPOON_API}/recipes/complexSearch?sort=popularity&number=100&apiKey=${API_KEY}`);
    for (let r=0; r<5; r++) {
        let randNum = Math.floor(Math.random() * 100) + 1;
        let randRecipeId = popularRecipes.data.results[randNum].id;
        const randRecipe = await axios.get(`${SPOON_API}/recipes/${randRecipeId}/information?apiKey=${API_KEY}`);
        let name = randRecipe.data.title;
        let image = randRecipe.data.image;
        let time = randRecipe.data.readyInMinutes;
        let diets = randRecipe.data.diets;
        let container = "popular"
        handleRecipe(name, image, time, diets, container);
    }

    const healthyRecipes = await axios.get(`${SPOON_API}/recipes/complexSearch?sort=healthiness&number=100&apiKey=${API_KEY}`);
    for (let r=0; r<5; r++) {
        let randNum = Math.floor(Math.random() * 100) + 1;
        let randRecipeId = healthyRecipes.data.results[randNum].id;
        const randRecipe = await axios.get(`${SPOON_API}/recipes/${randRecipeId}/information?apiKey=${API_KEY}`);
        let name = randRecipe.data.title;
        let image = randRecipe.data.image;
        let time = randRecipe.data.readyInMinutes;
        let diets = randRecipe.data.diets;
        let container = "healthy"
        handleRecipe(name, image, time, diets, container);
    }

  }

async function handleRecipe(name, image, time, diets, container) {
    let recipe = `
            <div id="${name}">
                <a href="/"> <img class="recipe-pic" src="${image}"/></a>
                <h3>${name}</h3>
                <p>Cook Time: ${time} minutes</p>
            </div>
        `;
     $(`#${container}-recipes`).append(recipe);

}