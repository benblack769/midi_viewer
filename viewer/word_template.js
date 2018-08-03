var input_json_data = null;
var word_mapping = null;//new Map(input_json_data.map(dict=>[dict.chord_repr,dict]))
//input_json_data.forEach(function(dict){word_mapping[dict.chord_repr]=dict})
var word_list = null;//input_json_data.map(dict=>dict.chord_repr)
var numpy_vecs = null;

var xsize = 800;
var ysize = 600;
var graphics = [];

function copyToClipboard(str){
    const el = document.createElement('textarea');
    el.value = str;
    el.setAttribute('readonly', '');
    el.style.position = 'absolute';
    el.style.left = '-9999px';
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
}
function get_vector(chord_repr){
	var idx = word_list.indexOf(chord_repr)
	var vec = numpy_vecs[idx]
	return vec
}
function add_to_dropdown_menu(parent_element, choices_list){
    for(var i = 0; i < choices_list.length; i++) {
        var opt = document.createElement('option');
        opt.innerHTML = choices_list[i];
        opt.value = choices_list[i];
        parent_element.append(opt);
    }
}
function play_audio(source_name){
    MIDIjs.play("midi_text_midi_files/"+source_name+".mid")
}
function clear_red_circ(parent_id){
	d3.select(parent_id).selectAll("*").remove()
}
function draw_red_circ(parent_id,cx,cy){
	clear_red_circ(parent_id)

	d3.select(parent_id).append('circle')
		.attr("cx", cx)
		.attr("cy", cy)
		.attr("r", 8)
		.attr("stroke", "red")
		.attr("fill", "rgba(0,0,0,0)")
		.attr("stroke-width", 3)
}
function select_word(chord){
	//document.getElementById("selected_display").value = ""
	if(word_mapping.has(chord)){
		var word_idx = word_list.indexOf(chord)
        var word_data = input_json_data[word_idx]

		redraw_red_circ(word_data.x,word_data.y)

		document.getElementById("selected_display").value = chord
	}
}
function handle_selection(){
	d3.select("#data_plot svg").append('g')
			.attr("id","data_select")
	$("#selected_display").change(function(){
		select_word($(this).val())
	})
}
function handle_calculation(){
    $("#play_button").click(function(){
        var this_val = $('#play_input_el').val() // get the current value of the input field.
        if(word_mapping.has(this_val)){
            play_audio(word_mapping.get(this_val).chord)
        }
    })
	$(".analogy_calc").change(function(){
		var val1 = $('#analogy1_in').val()
		var val2 = $('#analogy2_in').val()
		var val3 = $('#analogy3_in').val()
		var result;
		if(word_mapping.has(val1) &&
	       word_mapping.has(val2) &&
	       word_mapping.has(val3)){
			var target = add_vecs(sub_vecs(get_vector(val1),get_vector(val2)),get_vector(val3));
			var result_idx = closest(numpy_vecs,target,cosine_d);
			console.log(target)
			console.log(result_idx)
			console.log(word_list.length)
			result = word_list[result_idx]
	    }
		else{
			result = "";
		}
		document.getElementById("analogy_res").innerText = result;
	})
	$(".dist_calc").change(function(){
		var val1 = $('#distance1_in').val()
		var val2 = $('#distance2_in').val()
		var result;
		if(word_mapping.has(val1) &&
	       word_mapping.has(val2)){
			result = cosine_d(get_vector(val1),get_vector(val2))
	    }
		else{
			result = "";
		}
		document.getElementById("dist_res").innerText = result;
	})
}
function redraw_red_circ(xval, yval){
	var display_point = {
		x: graphics[0].scales.X(xval),
		y: graphics[0].scales.Y(yval),
	}
	draw_red_circ("#data_select",display_point.x,display_point.y);
}
function make_graphic(input_data){
	var data_graphic = {
      title: "Musica",
      //description: "Yearly UFO sightings from 1945 to 2010.",
      data: input_data,
      width: xsize,
      height: ysize,
      target: "#data_plot",
      x_accessor: "x",
      y_accessor: "y",
      chart_type:'point',
      brush: 'xy',
      //missing_is_hidden: true,
	  click_to_zoom_out: false,
      //brush: 'xy',
	  zoom_callback:function(){
          select_word($("#selected_display").val())
	  },
      mouseover: function(d, i) {
            // custom format the rollover text, show days
            d3.select('#data_plot svg .mg-active-datapoint')
                .text(d.data.chord_repr);
        },
	  click: function(d,i) {
        select_word(d.data.chord_repr)
        play_audio(d.data.chord)
    }
    }
    graphics.push(data_graphic);
	MG.data_graphic(graphics[0])
	$("#zoom_out_button").click(function(){
		MG.zoom_to_raw_range(data_graphic)
	})
}
function load_data(){
    $.getJSON("view_data.json",function(json){
        input_json_data = json;
        word_mapping = new Map(input_json_data.map(dict=>[dict.chord_repr,dict]))
        word_list = input_json_data.map(dict=>dict.chord_repr)
        add_to_dropdown_menu($("#song_list"),word_list)
        make_graphic(input_json_data)
    	handle_calculation()
    	handle_selection()
    })
	$.getJSON("vec_json.json",function(json){
		numpy_vecs = json;
		$(".vec_calc_elmt").show();
	})
}

//function make_download_button()
$(document).ready(function(e) {
    load_data()
})
