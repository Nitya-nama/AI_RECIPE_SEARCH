const resultsContainer = document.getElementById("resultsContainer");
const addMessage = document.getElementById("addMessage");


// ======================================
// Render Recipes
// ======================================
function renderRecipes(recipes, showSimilarity = false) {
    resultsContainer.innerHTML = "";

    if (!recipes || recipes.length === 0) {
        resultsContainer.innerHTML = "<p>No recipes found.</p>";
        return;
    }

    recipes.forEach(r => {
        const card = document.createElement("article");
        card.className = "recipe-card";

        const title = document.createElement("h3");
        title.textContent = r.title || "Untitled recipe";
        card.appendChild(title);

        const meta = document.createElement("p");
        meta.className = "meta";
        meta.textContent =
            (r.cuisine || "Unknown cuisine") +
            " · " +
            (r.difficulty || "Difficulty N/A") +
            " · " +
            (r.cook_time || "Time N/A") + " min";
        card.appendChild(meta);

        if (showSimilarity && typeof r.similarity === "number") {
            const sim = document.createElement("p");
            sim.className = "similarity";
            sim.textContent = "Similarity: " + r.similarity.toFixed(3);
            card.appendChild(sim);
        }

        if (r.diet_tags && r.diet_tags.length > 0) {
            const tagsP = document.createElement("p");
            tagsP.className = "tags";
            r.diet_tags.forEach(t => {
                const span = document.createElement("span");
                span.className = "tag";
                span.textContent = t;
                tagsP.appendChild(span);
            });
            card.appendChild(tagsP);
        }

        if (r.ingredients && r.ingredients.length > 0) {
            const ingTitle = document.createElement("h4");
            ingTitle.textContent = "Ingredients";
            card.appendChild(ingTitle);

            const ul = document.createElement("ul");
            r.ingredients.forEach(ing => {
                const li = document.createElement("li");
                li.textContent =
                    (ing.name || "") +
                    (ing.quantity ? ` – ${ing.quantity}` : "") +
                    (ing.unit ? ` ${ing.unit}` : "");
                ul.appendChild(li);
            });
            card.appendChild(ul);
        }

        if (r.steps && r.steps.length > 0) {
            const stepsTitle = document.createElement("h4");
            stepsTitle.textContent = "Steps";
            card.appendChild(stepsTitle);

            const ol = document.createElement("ol");
            r.steps.forEach(step => {
                const li = document.createElement("li");
                li.textContent = step;
                ol.appendChild(li);
            });
            card.appendChild(ol);
        }

        resultsContainer.appendChild(card);
    });
}



// ======================================
// Add Recipe Form
// ======================================
document.getElementById("addRecipeForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    addMessage.textContent = "";

    const title = document.getElementById("title").value;
    const description = document.getElementById("description").value;
    const cuisine = document.getElementById("cuisine").value;
    const difficulty = document.getElementById("difficulty").value;
    const cook_time = document.getElementById("cook_time").value;
    const diet_tags = document.getElementById("diet_tags").value;
    const ingredientsText = document.getElementById("ingredients").value;
    const stepsText = document.getElementById("steps").value;

    // Parse ingredients textarea
    const ingredients = [];
    ingredientsText.split("\n").forEach(line => {
        const parts = line.split("|").map(p => p.trim());
        if (parts[0]) {
            ingredients.push({
                name: parts[0],
                quantity: parts[1] || "",
                unit: parts[2] || ""
            });
        }
    });

    const payload = {
        title,
        description,
        cuisine,
        difficulty,
        cook_time: cook_time ? Number(cook_time) : null,
        diet_tags,
        ingredients,
        steps: stepsText
    };

    try {
        const res = await fetch("/api/recipes", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok) {
            addMessage.textContent = data.error || "Failed to add recipe.";
            addMessage.className = "message error";
            return;
        }

        addMessage.textContent = "Recipe saved!";
        addMessage.className = "message success";
        document.getElementById("addRecipeForm").reset();
    } catch (err) {
        console.error(err);
        addMessage.textContent = "Error connecting to server.";
        addMessage.className = "message error";
    }
});



// ======================================
// Ingredient Search
// ======================================
document.getElementById("ingredientSearchForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const include = document.getElementById("includeIngredients").value;
    const exclude = document.getElementById("excludeIngredients").value;
    const cuisine = document.getElementById("searchCuisine").value;
    const diet_tag = document.getElementById("searchDietTag").value;

    const params = new URLSearchParams();
    if (include) params.append("include", include);
    if (exclude) params.append("exclude", exclude);
    if (cuisine) params.append("cuisine", cuisine);
    if (diet_tag) params.append("diet_tag", diet_tag);

    try {
        const res = await fetch("/api/recipes/search-ingredients?" + params.toString());
        const data = await res.json();
        renderRecipes(data.results || []);
    } catch (err) {
        console.error(err);
        resultsContainer.innerHTML = "<p>Error during search.</p>";
    }
});



// ======================================
// Semantic Search
// ======================================
document.getElementById("semanticSearchForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const q = document.getElementById("semanticQuery").value;
    if (!q.trim()) return;

    const params = new URLSearchParams({ q });

    try {
        const res = await fetch("/api/recipes/search-semantic?" + params.toString());
        const data = await res.json();
        if (!res.ok) {
            resultsContainer.innerHTML = "<p>" + (data.error || "Semantic search failed.") + "</p>";
            return;
        }
        renderRecipes(data.results || [], true);
    } catch (err) {
        console.error(err);
        resultsContainer.innerHTML = "<p>Error during semantic search.</p>";
    }
});



// ======================================
// REFRESH BUTTON
// ======================================
document.getElementById("refreshBtn").addEventListener("click", () => {
    // Clear Add Recipe form
    document.getElementById("addRecipeForm").reset();

    // Clear Ingredient Search form
    document.getElementById("ingredientSearchForm").reset();

    // Clear Semantic Search form
    document.getElementById("semanticSearchForm").reset();

    // Clear results container
    resultsContainer.innerHTML = "";

    // Reset cuisine + diet dropdowns manually
    document.getElementById("searchCuisine").value = "";
    document.getElementById("searchDietTag").value = "";

    // Clear any success/error messages
    addMessage.textContent = "";
});




// ======================================
// DARK / LIGHT MODE TOGGLE
// ======================================
const themeBtn = document.getElementById("themeToggle");

themeBtn.addEventListener("click", () => {
    document.body.classList.toggle("light-mode");

    if (document.body.classList.contains("light-mode")) {
        themeBtn.textContent = "🌑 Dark Mode";
    } else {
        themeBtn.textContent = "🌙 Light Mode";
    }
});
