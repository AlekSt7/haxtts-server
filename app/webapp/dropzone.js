const inputElement = document.querySelector('.drop-zone__input');
const dropZoneElement = inputElement.closest(".drop-zone");

dropZoneElement.addEventListener("click", (e) => {
    inputElement.click();
});

inputElement.addEventListener("change", (e) => {
    if (inputElement.files.length) {
    updateThumbnail(inputElement.files[0]);
    inputElement.files = inputElement.files;
    }
});

dropZoneElement.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZoneElement.classList.add("drop-zone--over");
});

["dragleave", "dragend"].forEach((type) => {
    dropZoneElement.addEventListener(type, (e) => {
        dropZoneElement.classList.remove("drop-zone--over");
    });
});

dropZoneElement.addEventListener("drop", (e) => {
    e.preventDefault();

    if (e.dataTransfer.files.length) {
        inputElement.files = e.dataTransfer.files;
        updateThumbnail(e.dataTransfer.files[0]);
        inputElement.files = e.dataTransfer.files;
    }

    dropZoneElement.classList.remove("drop-zone--over");
});

/**
 * Updates the thumbnail on a drop zone element.
 *
 * @param {File|null} file
 */
function updateThumbnail(file) {
    let thumbnailElement = dropZoneElement.querySelector(".drop-zone__thumb");

    // If file is null, remove the thumbnail and restore the hint
    if (file === null) {
        if (thumbnailElement) {
            dropZoneElement.removeChild(thumbnailElement);
        }
        dropZoneElement.appendChild(createHint()); // Restore the hint
        return;
    }

    // First time - remove the hint
    if (dropZoneElement.querySelector(".drop-zone__hint")) {
        dropZoneElement.querySelector(".drop-zone__hint").remove();
    }

    // First time - there is no thumbnail element, so lets create it
    if (!thumbnailElement) {
        thumbnailElement = document.createElement("div");
        thumbnailElement.classList.add("drop-zone__thumb");

        // Создаем текстовое содержимое с именем файла
        const fileNameElement = document.createElement("span");
        fileNameElement.textContent = file.name;
        thumbnailElement.appendChild(fileNameElement);

        dropZoneElement.appendChild(thumbnailElement);
    } else {
        // If the thumbnail already exists, update only the file name
        const fileName = thumbnailElement.querySelector("span");
        if (fileName) {
            fileName.textContent = file.name;
        }
    }
}

function createHint() {
    const hint = document.createElement("span");
    hint.classList.add("drop-zone__hint");
    hint.textContent = "Drop .wav file here or click to upload";
    return hint;
}