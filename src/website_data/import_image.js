/*** Global structure definition ***/

let image_vis = document.getElementById('image_vis');
let upload_info = document.getElementById('upload_info');
let drop_info = document.getElementById('drop_info');
let dropped_image = document.getElementById('dropped_image');

var image_in = null; /* Global variable (Base64 Image), shared with all '.js' files */

let MAX_HEIGHT = 450;

let file_select_dialog = document.createElement('input'); /* File selection dialog */
file_select_dialog.type = 'file';

let reader = new FileReader(); /* Input image reader */


/*** Pre-defined functions ***/

function prevent_defaut_behaviour(event){
	event.preventDefault();
}


function dragleave_image(){
	if(image_in != null){
		dropped_image.style.display = 'block';
	}
	else {
		upload_info.style.display = 'block';
		image_vis.style.border = '5px dashed #EBA3A1';
	}

	drop_info.style.display = 'none';
}


function render(src){
	let image = new Image();

	image.onload = function(){
		if(image.height > MAX_HEIGHT) { /* Resize (only vizually) the image with keeping its aspect ratio */
			image.width *= MAX_HEIGHT / image.height;
			image.height = MAX_HEIGHT;
		}

		image_vis.style.width = image.width + 'px';
		image_vis.style.height = image.height + 'px';

		let ctx = dropped_image.getContext("2d");

		dropped_image.width = image.width;
		dropped_image.height = image.height;
		ctx.drawImage(image, 0, 0, image.width, image.height);
	};

	image_in = src;
	image.src = src;

	upload_info.style.display = 'none';

	dropped_image.style.display = 'block';

	image_vis.style.border = '5px solid #E5322D';

	selected_params['image_in'] = image_in; /* Variable from "input_data.js" */
	start_pred_verify(); /* Function from "input_data.js" */
}


function dragenter_image(){
	if(image_in != null){
		dropped_image.style.display = 'none';
	}

	upload_info.style.display = 'none';
	drop_info.innerText = 'Drop your image!';
	drop_info.style.display = 'block';
	image_vis.style.border = '5px solid #E5322D';
}


function onload_reader(event){
	render(event.target.result);
}


function drop_image(event){
	src = event.dataTransfer.files[0];

	if(! src.type.startsWith('image')){
		dragleave_image();
		return; /* Dropped file is not an image */
	}

	drop_info.style.display = 'none';

	reader.readAsDataURL(src);
}


function click_image_visualization(){
	file_select_dialog.click();
}


function change_file_select_dialog(){
	if(this.files.length > 0){
		if(this.files[0].type.startsWith('image'))
			reader.readAsDataURL(this.files[0]);
	}
}


/*** Events assignement ***/

window.addEventListener('dragover', prevent_defaut_behaviour);
window.addEventListener('drop', prevent_defaut_behaviour);

reader.addEventListener('load', onload_reader);

image_vis.addEventListener('click', click_image_visualization);
image_vis.addEventListener('dragenter', dragenter_image);
image_vis.addEventListener('dragleave', dragleave_image);
image_vis.addEventListener('drop', drop_image);

file_select_dialog.addEventListener('change', change_file_select_dialog);
