const snapFile = document.getElementById("snap-file");
const fileBtn = document.getElementById("file-btn");
const preview = document.getElementById("preview");
const previewContainer = document.getElementById("preview-container");
const removeImage = document.getElementById("removeImage");
fileBtn.addEventListener("click", () => {
  snapFile.click();
});

snapFile.addEventListener('change',()=>{
    
   const file=snapFile.files[0]
   console.log(file)
  
   if (!file){
    return 
   }
   preview.src=URL.createObjectURL(file)
   previewContainer.classList.remove("hidden")
})

removeImage.addEventListener('click',()=>{
    snapFile.value=""
    preview.src=""
    previewContainer.classList.add('hidden')
})
