/* Django server's main address */
let root_address = 'http://127.0.0.1:8000/';


/*** Initialization ***/

let xhr = new XMLHttpRequest();

let output_display = {};

output_display['out_image_vis'] = document.querySelector('#out_image_vis canvas');

output_display['classification'] = {};
output_display['classification']['pred_category'] = document.querySelector('#pred_category input');
output_display['classification']['detailed_res'] = document.querySelector('.table_container tbody');

output_display['interpretation'] = {};
output_display['interpretation']['img_caption'] = document.querySelector('#img_caption textarea');
output_display['interpretation']['img_graph'] = document.querySelector('#img_graph canvas');


/*** Pre-defined functions ***/

function get_output_result(send_json){
	xhr.open('POST', root_address+'scenes_tool/');

	xhr.setRequestHeader('Content-Type', 'application/json');

	xhr.send(send_json);
}


function detected_objects_image_display(base64_encoded_image){
	let context = output_display['out_image_vis'].getContext('2d');

	let out_image_vis = new Image();

	out_image_vis.onload = function() {
		if(out_image_vis.height > MAX_HEIGHT) { /* Resize (only vizually) the image with keeping its aspect ratio */
			out_image_vis.width *= MAX_HEIGHT / out_image_vis.height;
			out_image_vis.height = MAX_HEIGHT;
		}

		output_display['out_image_vis'].width = out_image_vis.width;
		output_display['out_image_vis'].height = out_image_vis.height;

		context.drawImage(out_image_vis, 0, 0, out_image_vis.width, out_image_vis.height);
	};

	out_image_vis.src = 'data:image/png;base64,' + base64_encoded_image;
}


function classification_task_output_display(categories_probas){
	output_display['classification']['pred_category'].value = categories_probas[0][0];

	let detailed_res = '';

	for(let i=0; i<categories_probas.length; i++){
		detailed_res += '<tr>';
		detailed_res += '<td>' + (i+1) + '</td>';
		detailed_res += '<td>' + categories_probas[i][0] + '</td>';
		detailed_res += '<td>' + categories_probas[i][1] + ' %</td>';
		detailed_res += '</tr>\n';
	}

	output_display['classification']['detailed_res'].innerHTML = detailed_res;
}


function interpretation_task_output_display(img_caption, img_graph){
	output_display['interpretation']['img_caption'].value = img_caption;

	/* Display 'scene graph' */
	let context = output_display['interpretation']['img_graph'].getContext('2d');

	let out_image_vis = new Image();

	out_image_vis.onload = function() {
		if(out_image_vis.height > MAX_HEIGHT) { /* Resize (only vizually) the image with keeping its aspect ratio */
			out_image_vis.width *= MAX_HEIGHT / out_image_vis.height;
			out_image_vis.height = MAX_HEIGHT;
		}

		output_display['interpretation']['img_graph'].width = out_image_vis.width;
		output_display['interpretation']['img_graph'].height = out_image_vis.height;

		context.drawImage(out_image_vis, 0, 0, out_image_vis.width, out_image_vis.height);
	};

	out_image_vis.src = 'data:image/png;base64,' + img_graph;
}


function load_xhr(){
	if (xhr.readyState === 4 && xhr.status === 200) {
		let response = JSON.parse(xhr.responseText);

		detected_objects_image_display(response['image']);

		if(selected_params['task'] == 'classification'){
			classification_task_output_display(response['categories_probas']);
		}
		else{
			interpretation_task_output_display(response['description'], response['scene_graph']);
		}

		show_output_results(); /* Function from 'input_data.js' */
	}
}


/*** Events assignement ***/

xhr.addEventListener('load', load_xhr);
