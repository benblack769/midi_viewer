var word_mapping = new Map(input_json_data.map(dict=>[dict.chord_repr,dict]))
//input_json_data.forEach(function(dict){word_mapping[dict.chord_repr]=dict})
var word_list = input_json_data.map(dict=>dict.chord_repr)
var numpy_vecs = null;

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
function create_sel_circ(curpoint){
	var svgNS = "http://www.w3.org/2000/svg";
	var circ = document.createElementNS(svgNS,'circle')
	circ.setAttributeNS(null,"cx",curpoint.attr('cx'));
	circ.setAttributeNS(null,"cx",curpoint.attr('cy'));
	circ.setAttributeNS(null,"r",10);
	circ.setAttributeNS(null,"stroke","red");
	circ.setAttributeNS(null,"fill","");
	circ.setAttributeNS(null,"stroke-width",3);
	//circ["stroke-width"]= 3
	console.log(circ)
	return circ
}
function select_word(chord){
	d3.select("#display_select").selectAll("*").remove()
	//document.getElementById("selected_display").value = ""
	if(word_mapping.has(chord)){
		var idx = word_list.indexOf(chord)

		var point_dom_elmt = $('circle.path-'+idx)
		console.log(point_dom_elmt)
		d3.select("#display_select").append('circle')
			.attr("cx", point_dom_elmt.attr("cx"))
			.attr("cy", point_dom_elmt.attr("cy"))
			.attr("r", 8)
			.attr("stroke", "red")
			.attr("fill", "rgba(0,0,0,0)")
			.attr("stroke-width", 3)

		document.getElementById("selected_display").value = chord
	}
}
function handle_selection(){
	d3.select("svg").append('g')
			.attr("id","display_select")
    var voronoi_cells = d3.selectAll('.mg-voronoi path');
    voronoi_cells.on('click', function(d,i) {
        //console.log(d.data)
		//create_sel_circ(point_dom_elmt))
        select_word(d.data.chord_repr)
        play_audio(d.data.chord)
        //document.getElementById("selected_display").innerText = d.data.chord_repr
    });
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
function make_graphic(){
    MG.data_graphic({
      title: "Musica",
      //description: "Yearly UFO sightings from 1945 to 2010.",
      data: input_json_data,
      width: 800,
      height: 600,
      target: "#data_plot",
      x_accessor: "x",
      y_accessor: "y",
      chart_type:'point',
      //click_to_zoom_out: false,
      //brush: 'xy',
        mouseover: function(d, i) {
            // custom format the rollover text, show days
            d3.select('#data_plot svg .mg-active-datapoint')
                .text(d.data.chord_repr);
        },
    });
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
