var first_image = true;

function sendRequest(route, resultHandler) {
  // Get the data to send to the server
  var settings = {
    sampler_name: document.getElementById("setting-sampler").value,
    steps: document.getElementById("setting-steps").value,
    height: document.getElementById("setting-height").value,
    width: document.getElementById("setting-width").value,
    cfg_scale: document.getElementById("setting-cfg").value,
    seed: document.getElementById("setting-seed").value,
  };
  console.log(settings);
  var data = {
    user_prompt: document.getElementById("prompt").value,
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
      console.log(result);
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
  fetch("/api/progress")
    .then((response) => response.json())
    .then((data) => {
      let progress = data.progress;
      // document.getElementById("progress-bar").style.width = progress + "%";
      document.querySelector("#generation-progress > div").style.width = progress + "%";
      document.querySelector("#generation-progress > div").innerHTML = progress + "%";
      if (first_image && progress < 100) {
        setTimeout(updateProgress, 500); // Check progress every second
      }
    });
}

document.getElementById("generate").addEventListener("click", function () {
  first_image = true;
  sendRequest("/api/get_image", function (result) {
    let response = result;
    setInnerHTML(
      ["#user-prompt", "#optimized-prompt"],
      [response.user_prompt, response.optimized_prompt]
    );
    document.querySelector("#user-image img").setAttribute("src", response.user_image);
    document.querySelector("#optimized-image img").setAttribute("src", response.optimized_image);
    document.getElementById("images").classList.remove("hidden");
    first_image = false;
  });
  updateProgress();
});
