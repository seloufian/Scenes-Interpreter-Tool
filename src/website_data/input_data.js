/*** Global structure definition ***/

let part_btn = {};
part_btn['in'] = document.getElementById('input_btn');
part_btn['out'] = document.getElementById('output_btn');

let out_task = {};
out_task['classification'] = document.getElementById('out_classif');
out_task['interpretation'] = document.getElementById('out_interp');

let task_btn = {};
task_btn['classification'] = document.getElementById('sel_class');
task_btn['interpretation'] = document.getElementById('sel_inter');

let temp_array, params_dict = {};

temp_array = [...document.querySelectorAll('#param_dataset > button')];
params_dict['param_dataset'] = Object.fromEntries(temp_array.map(x => [x.textContent.toLowerCase(), x]));

temp_array = [...document.querySelectorAll('#param_enrichment > button')];
params_dict['param_enrichment'] = Object.fromEntries(temp_array.map(x => [x.textContent.toLowerCase(), x]));

let param_type = {};
param_type['param_dataset'] = document.querySelector('#param_dataset > p');
param_type['param_enrichment'] = document.querySelector('#param_enrichment > p');

let start_prediction_btn = document.getElementById('start_tool');

let input_data = document.getElementById('input_data');
let output_data = document.getElementById('output_data');
let wait_frame = document.getElementById('wait_frame');

let task_style = {};
task_style['enabled'] = 'border-bottom: 5px solid #E5322D; padding-bottom: 0px;';
task_style['disabled'] = 'border-bottom: none; padding-bottom: 5px;';

let param_style = {};
param_style['focus'] = 'border-color: #E5322D;';
param_style['blur'] = 'border-color: #B5B5B6;';

let click_btn_style = {};
click_btn_style['enabled'] = 'background: #E5322D; color: #FFFFFF;';
click_btn_style['disabled'] = 'background: #FFFFFF; color: #000000;';


/*** Initialization ***/

part_btn['in'].style.cssText = task_style['enabled'];
part_btn['out'].disabled = true;

task_btn['classification'].style.cssText = task_style['enabled'];

start_prediction_btn.disabled = true;

let selected_params = {};
selected_params['part'] = 'input';
selected_params['task'] = 'classification';
selected_params['image_in'] = null;
selected_params['param_dataset'] = null;
selected_params['param_enrichment'] = null;


/*** Pre-defined functions ***/

function blur_params_marks(keep_name){
	param_type[keep_name].style.cssText = param_style['focus'];

	for(let key in param_type){
		if(key != keep_name)
			param_type[key].style.cssText = param_style['blur'];
	}
}


function enable_enrichment(value=true){
	if(value){
		params_dict['param_enrichment']['no'].disabled = false;
		params_dict['param_enrichment']['yes'].disabled = false;
	}
	else{
		params_dict['param_enrichment']['no'].disabled = true;
		params_dict['param_enrichment']['yes'].disabled = true;
	}
}

/* Switch between "Classification" and "Interpretation" */

function click_action(event){
	let clicked_name = event.target.textContent.toLowerCase();

	task_btn[clicked_name].style.cssText = task_style['enabled'];

	if(clicked_name == 'classification'){
		selected_params['task'] = 'classification';

		task_btn['interpretation'].style.cssText = task_style['disabled'];
		param_type['param_dataset'].parentNode.style.display = 'block';
		start_prediction_btn.innerHTML = 'Start classification<br>and show results';

		if(selected_params['param_dataset'] == 'mit-indoor'){ /* TODO: Review the -messy- code in condition */
			let event = {target: {textContent: 'mit-indoor'}};
			click_dataset(event);
		}
	}
	else{
		selected_params['task'] = 'interpretation';

		enable_enrichment();

		task_btn['classification'].style.cssText = task_style['disabled'];

		selected_params['param_dataset'] = 'mit-indoor';
		param_type['param_dataset'].parentNode.style.display = 'none';

		start_prediction_btn.innerHTML = 'Start interpretation<br>and show results';

		selected_params['param_dataset'] = 'mit-indoor';
	}
}

/* "Start prediction" verification */

function start_pred_verify(){
	let allow_start_pred = true;

	allow_start_pred = selected_params['image_in'] != null;

	allow_start_pred = selected_params['param_dataset'] != null;

	/* Check 'enrichment selection' only with MIT-Indoor dataset */
	if(selected_params['param_dataset'] == 'mit-indoor'){
		allow_start_pred = selected_params['param_enrichment'] != null;
	}

	start_prediction_btn.disabled = !allow_start_pred;
}

/* Parameters selection */

function click_dataset(event){
	let clicked_name = event.target.textContent.toLowerCase();

	selected_params['param_dataset'] = clicked_name;

	params_dict['param_dataset'][clicked_name].style.cssText = click_btn_style['enabled'];

	blur_params_marks('param_dataset');

	if(clicked_name == 'mit-indoor'){
		params_dict['param_dataset']['sun2012'].style.cssText = click_btn_style['disabled'];
		enable_enrichment();
	}
	else{
		params_dict['param_dataset']['mit-indoor'].style.cssText = click_btn_style['disabled'];
		enable_enrichment(false);
	}

	start_pred_verify();
}


function click_enrichment(event){
	let clicked_name = event.target.textContent.toLowerCase();

	selected_params['param_enrichment'] = clicked_name;

	params_dict['param_enrichment'][clicked_name].style.cssText = click_btn_style['enabled'];

	blur_params_marks('param_enrichment');

	if(clicked_name == 'yes'){
		params_dict['param_enrichment']['no'].style.cssText = click_btn_style['disabled'];
	}
	else{
		params_dict['param_enrichment']['yes'].style.cssText = click_btn_style['disabled'];
	}

	start_pred_verify();
}


function show_wait_frame(){
	part_btn['out'].disabled = true;

	input_data.style.display = 'none';
	output_data.style.display = 'none';

	wait_frame.innerHTML = 'Please wait until<br>' + selected_params['task'] + ' process finish!';
	wait_frame.style.display = 'block';
}


function show_output_results(){
	wait_frame.style.display = 'none';

	part_btn['out'].disabled = false;

	part_btn['out'].style.cssText = task_style['enabled'];
	part_btn['in'].style.cssText = task_style['disabled'];

	input_data.style.display = 'none';
	output_data.style.display = 'block';

	if(selected_params['task'] == 'classification'){
		out_task['classification'].style.display = 'block';
		out_task['interpretation'].style.display = 'none';
	}
	else {
		out_task['classification'].style.display = 'none';
		out_task['interpretation'].style.display = 'block';
	}

	selected_params['part'] = 'output';
}


function click_start_prediction(){
	show_wait_frame();

	let send_json = JSON.stringify(selected_params);

	get_output_result(send_json); /* Function from "output_data.js" */
}

/* Switch between "Input image and parameter tuning" and "Detailed results" */

function click_change_part(event){
	let clicked_name = event.target.id.toLowerCase();

	if(clicked_name == 'input_btn'){
		if(selected_params['part'] == 'output'){
			part_btn['out'].style.cssText = task_style['disabled'];
			part_btn['in'].style.cssText = task_style['enabled'];

			input_data.style.display = 'block';
			output_data.style.display = 'none';

			selected_params['part'] = 'input';
		}
	}
	else{
		if(selected_params['part'] == 'input'){
			part_btn['out'].style.cssText = task_style['enabled'];
			part_btn['in'].style.cssText = task_style['disabled'];

			input_data.style.display = 'none';
			output_data.style.display = 'block';

			selected_params['part'] = 'output';
		}
	}
}


/*** Events assignement ***/

task_btn['classification'].addEventListener('click', click_action);
task_btn['interpretation'].addEventListener('click', click_action);

params_dict['param_dataset']['mit-indoor'].addEventListener('click', click_dataset);
params_dict['param_dataset']['sun2012'].addEventListener('click', click_dataset);

params_dict['param_enrichment']['yes'].addEventListener('click', click_enrichment);
params_dict['param_enrichment']['no'].addEventListener('click', click_enrichment);

start_prediction_btn.addEventListener('click', click_start_prediction);

part_btn['in'].addEventListener('click', click_change_part);
part_btn['out'].addEventListener('click', click_change_part);
