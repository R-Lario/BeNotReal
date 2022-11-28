function fadeOutEffect(target) {
    let fadeEffect = setInterval(function () {
        if (!target.style.opacity) {
            target.style.opacity = 1;
        }
        if (target.style.opacity > 0) {
            target.style.opacity -= 0.02;
        } else {
            clearInterval(fadeEffect);
            target.innerHTML = ""
        }
    }, 30);
}


document.addEventListener("DOMContentLoaded", () => {
    //remove flash messages
    let flash_messages = document.querySelector(".flash-messages")
    if (flash_messages) {
        setTimeout(function() {
            fadeOutEffect(flash_messages);
        }, 2000);
    }

    //Include own berealproccess in the app
    let ownBereal = document.querySelector(".users-own-post");
    if (ownBereal)
    {
        let firstPosition = document.querySelector(".not-posted-yet");
        firstPosition.innerHTML = ownBereal.innerHTML;
        firstPosition.classList.remove("not-posted-yet");
        ownBereal.remove();
    }

    //make the bereals switch images
    let posts = document.querySelectorAll(".bereal-image")
    posts.forEach((post) =>  {
        post.addEventListener("click", () => {
            // save the src's
            let parentDiv = post.parentElement
            let images = parentDiv.querySelectorAll(".bereal-image");

            let secondImageSrc = images[0]["src"];
            let firstImageSrc = images[1]["src"];

            //switch src's
            images[0]["src"] = firstImageSrc;
            images[1]["src"] = secondImageSrc;
        });
    });
});