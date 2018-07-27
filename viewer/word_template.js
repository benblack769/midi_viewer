var word_mapping = new Map(input_json_data.map(dict=>[dict.chord_repr,dict]))
//input_json_data.forEach(function(dict){word_mapping[dict.chord_repr]=dict})
var word_list = input_json_data.map(dict=>dict.chord_repr)
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
	clear_red_circ("#overview_select")
	//document.getElementById("selected_display").value = ""
	if(word_mapping.has(chord)){
		var word_idx = word_list.indexOf(chord)

		var point_dom_elmt = $('#overview_plot svg g.mg-points circle.path-'+word_idx)

		draw_red_circ("#overview_select",point_dom_elmt.attr("cx"),point_dom_elmt.attr("cy"))

		redraw_red_circ()

		document.getElementById("selected_display").value = chord
	}
}
function handle_selection(){
	d3.select("#overview_plot svg").append('g')
			.attr("id","overview_select")

	$("#overview_plot").hide()
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
    add_to_dropdown_menu($("#song_list"),word_list)
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
function redraw_red_circ(){
	var elmt = $("#overview_select circle")[0]
	if(!elmt){
		return;
	}
	//console.log(elmt)
	var point = {
		x: elmt.cx.baseVal.value,
		y: elmt.cy.baseVal.value,
	}
	var data_point = {
		x: graphics[1].scales.X.invert(point.x),
		y: graphics[1].scales.Y.invert(point.y),
	}
	var display_point = {
		x: graphics[0].scales.X(data_point.x),
		y: graphics[0].scales.Y(data_point.y),
	}
	draw_red_circ("#data_select",display_point.x,display_point.y);
}
function make_graphic(){
	var data_graphic = {
      title: "Musica",
      //description: "Yearly UFO sightings from 1945 to 2010.",
      data: input_json_data,
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
		redraw_red_circ()
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
	graphics.push({
      title: "Musica",
      //description: "Yearly UFO sightings from 1945 to 2010.",
      data: input_json_data,
      width: 400,
      height: 300,
        top: 20,
        bottom: 20,
        right: 0,
        left: 0,
      target: "#overview_plot",
      x_accessor: "x",
      y_accessor: "y",
      chart_type:'point',
	  zoom_target: data_graphic,
      brush: 'xy',
        x_axis: false,
        y_axis: false,
        showActivePoint: false,
    });
	MG.data_graphic(graphics[0])
	MG.data_graphic(graphics[1])
	$("#zoom_out_button").click(function(){
		MG.zoom_to_raw_range(data_graphic)
	})
}


//function make_download_button()
$(document).ready(function(e) {
	$.getJSON("vec_json.json",function(json){
		numpy_vecs = json;
		$(".vec_calc_elmt").show();
	})
    make_graphic()
	handle_calculation()
	handle_selection()
})
