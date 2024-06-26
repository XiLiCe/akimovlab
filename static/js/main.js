const socket = io();

socket.on("connect", () => {
  console.log("Connected to the server");
});

socket.on("new_word", (data) => {
  const word = data.word;
  document.getElementById("new-prompt-textarea").textContent += word + " ";
});

socket.on("end_new_prompt", () => {
  document.getElementById("new-prompt-textarea").toggleAttribute("readonly");
  document.getElementById("settings").classList.remove("hidden");
  document.getElementById("images-container").classList.remove("hidden");
  generate_image_button.classList.remove("hidden");
  generate_image_button.toggleAttribute("disabled");
  back_button.toggleAttribute("disabled");
});

socket.on("disconnect", () => {
  console.log("Disconnected from the server");
});

var first_image = true;
var generate_text_button = document.getElementById("generate-prompt");
var generate_image_button = document.getElementById("generate-image");
var back_button = document.getElementById("back-button");

function sendRequest(route, resultHandler) {
  // Get the data to send to the server
  // Route: route to send request
  // resultHander: function called after getting response
  var settings = {
    sampler_name: document.getElementById("setting-sampler").value,
    steps: document.getElementById("setting-steps").value,
    height: document.getElementById("setting-height").value,
    width: document.getElementById("setting-width").value,
    cfg_scale: document.getElementById("setting-cfg").value,
    seed: document.getElementById("setting-seed").value,
    negative_prompt: "NSFW " + document.getElementById("negative_prompt").value,
  };
  var data = {
    user_prompt: document.getElementById("prompt").value,
    optimized_prompt: document.getElementById("new-prompt-textarea").value,
    settings: settings,
  };

  // Send a POST request to Flask route
  fetch(route, {
    method: "POST",
    body: JSON.stringify(data),
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((result) => {
      // Handle the result
      if ("error" in result) {
        alert(result.error);
        return;
      }
      resultHandler(result);
    })
    .catch((error) => {
      console.error(error);
    });
}

function setInnerHTML(selectors, values) {
  // Setting each selector it's value in values array
  selectors.forEach((selector, index) => {
    document.querySelector(selector).innerHTML = values[index];
  });
}

function updateProgress() {
  sendRequest("/api/progress", function (result) {
    let progress = result.progress.toFixed(2);
    document.querySelector("#generation-progress > div").style.width = progress + "%";
    document.querySelector("#generation-progress > div").innerHTML = progress + "%";
    if (first_image && progress < 100) {
      setTimeout(updateProgress, 1000); // Check progress every second
    }
  });
}

generate_text_button.addEventListener("click", function () {
  document.getElementById("text-generation").classList.add("hidden");
  document.getElementById("new-prompt").classList.remove("hidden");
  socket.emit("generate_prompt", { user_prompt: document.getElementById("prompt").value });
});

generate_image_button.addEventListener("click", function () {
  first_image = true;
  generate_image_button.toggleAttribute("disabled");
  back_button.toggleAttribute("disabled");
  sendRequest("/api/get_image", function (result) {
    let response = result;
    setInnerHTML(
      ["#user-prompt", "#optimized-prompt"],
      [response.user_prompt, response.optimized_prompt]
    );
    first_image = false;
    document.querySelector("#user-image img").setAttribute("src", response.user_image);
    document.querySelector("#optimized-image img").setAttribute("src", response.optimized_image);
    document.getElementById("images").classList.remove("hidden");
    generate_image_button.toggleAttribute("disabled");
    back_button.toggleAttribute("disabled");
  });
  updateProgress();
});

back_button.addEventListener("click", function () {
  document.getElementById("images-container").classList.add("hidden");
  document.getElementById("new-prompt").classList.add("hidden");
  document.getElementById("images").classList.add("hidden");
  document.getElementById("text-generation").classList.remove("hidden");
  document.getElementById("new-prompt-textarea").textContent = "";
  generate_image_button.toggleAttribute("disabled");
  back_button.toggleAttribute("disabled");

  // location.reload();
});
