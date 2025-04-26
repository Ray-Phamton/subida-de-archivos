document.addEventListener('DOMContentLoaded', function(){  
  const fileInput = document.getElementById('file-upload');
    const fileNameDisplay = document.getElementById('file-name');

    fileInput.addEventListener('change', function(){
        if (fileInput.files.length >= 0){
            fileNameDisplay.textContent = fileInput.files[0].name;
        } else {
            fileNameDisplay.textContent = 'Ningun archivo seleccionado'
        }    
    });
});    
