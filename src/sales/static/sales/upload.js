const csrf = document.getElementsByName("csrfmiddlewaretoken")[0].value
const alertBox = document.getElementById("alert-box")

const handleAlerts = (type, msg) =>{
    alertBox.innerHTML = `
    <div class="alert alert-${type}" role="alert">
        ${msg}
    </div>
    `
}

Dropzone.autoDiscover = false
const myDropZone = new Dropzone('#my-dropzone',{
    url: "/upload/",
    init : function(){
        this.on("sending", function(file, xhr, formData){
            console.log('sending')
            formData.append('csrfmiddlewaretoken', csrf)
        })
        this.on('success', function(file,response){
            const ex = response.ex
            if (ex){
                handleAlerts("danger","File alreadly Exists")
            }
            else{
                handleAlerts("success","Created Sucessfully")
            }
        })
    },
    mqxFiles: 3,
    maxFiles: 3,
    accecptedFiles: ".csv",
})