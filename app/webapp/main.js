        var currentFileForPlaying = null;
        var currentFileNameForPlaying = null;

        // Function to get the list of files
        async function fetchFiles() {
            const response = await fetch(`${apiUrl}/available-voices`);
            const files = await response.json();
            const speakersList = document.getElementById('speakersList');
            speakersList.innerHTML = '';

            files.forEach(fileName => {
                const li = document.createElement('li');

                const playButton = document.createElement('button');
                playButton.className += 'play-button';
                playButton.id += fileName;
                playButton.onclick = () => playFile(fileName);

                const playIcon = document.createElement('i');
                playIcon.className = 'fas fa-play';

                const deleteButton = document.createElement('button');
                deleteButton.className += 'delete-button';
                deleteButton.onclick = () => deleteFile(fileName);

                const deleteIcon = document.createElement('i');
                deleteIcon.className = 'fas fa-trash';

                deleteButton.appendChild(deleteIcon);
                playButton.appendChild(playIcon);
                li.appendChild(playButton);
                li.appendChild(document.createTextNode(fileName));
                li.appendChild(deleteButton);
                speakersList.appendChild(li);
            });
        }

        document.getElementById('upload-button').onclick = uploadFile;

        // Function for loading file
        async function uploadFile () {
            event.preventDefault();

            const fileInput = document.querySelector('.drop-zone__input');
            const file = fileInput.files[0];
            if(file != null) {
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);

                await fetch(`${apiUrl}/upload`, {
                    method: 'POST',
                    body: formData,
                });

                fileInput.value = '';
                updateThumbnail(null)
                fetchFiles();
            }
        }

        // Function to play a file
        function playFile(fileName) {
            var stop = false;
            if(currentFileNameForPlaying == fileName) stop = true;
            if (currentFileForPlaying != null) {
                changePlayButtonState(false, currentFileNameForPlaying);
                stopFile();
            }
            if(stop) return;
            currentFileForPlaying = new Audio(`${apiUrl}/files/${fileName}`);
            currentFileForPlaying.play();
            currentFileNameForPlaying = fileName
            changePlayButtonState(true, fileName);
            currentFileForPlaying.onended = () => {
                changePlayButtonState(false, fileName);
                stopFile();
            };
        }

        function changePlayButtonState(inPlay, fileName) {
            const button = document.getElementById(fileName)
            const playIcon = button.querySelector('.fas');
            if(inPlay) {
                playIcon.className = 'fas fa-stop';
            } else {
                playIcon.className = 'fas fa-play';
            }
        }

        function stopFile() {
             currentFileForPlaying.pause();
             currentFileForPlaying.currentTime = 0;
             currentFileForPlaying = null;
             currentFileNameForPlaying = null;
        }

        // Function to delete a file
        async function deleteFile(filename) {
            await fetch(`${apiUrl}/files/${filename}`, {
                method: 'DELETE',
            });
            fetchFiles(); // Refresh the file list after deletion
        }

        // Initialize the file list when the page loads
        window.onload = fetchFiles;