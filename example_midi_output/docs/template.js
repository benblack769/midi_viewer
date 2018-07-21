var filename_set = new Set(input_json_data.map(dict=>dict.filename))
function clicked_item(item){
    console.log(item)
    console.log("argg@!!!")
}
function make_indicies(){
    var l = input_json_data.length;
    var ind = new Array(l);
    for(var i = 0; i < l; i++){
        ind[i] = i;
    }
    return ind;
}
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
function add_to_dropdown_menu(parent_element, choices_list){
    for(var i = 0; i < choices_list.length; i++) {
        var opt = document.createElement('option');
        opt.innerHTML = choices_list[i];
        opt.value = choices_list[i];
        parent_element.appendChild(opt);
    }
}
function add_filename_data(filename){
    var display_queue = $(".mg-active-datapoint tspan").get(0)
    console.log(display_queue)
    var text_el = document.createElement('tspan');
    text_el.innerText = filename
    display_queue.appendChild(text_el)
}
function add_audio_player(source_name){
    var ogg_path = "midi_ogg_files/"+source_name+".ogg"
    var audio_player = '<audio controls>\
      <source src="'+ogg_path+'" type="audio/ogg">\
    Your browser does not support the audio element.\
    </audio>'
    document.getElementById("player_container").innerHTML = audio_player
}
function make_graphic(){
    MG.data_graphic({
      title: "Musica",
      //description: "Yearly UFO sightings from 1945 to 2010.",
      data: input_json_data,
      markers: make_indicies(),
      width: 400,
      height: 250,
      target: "#data_plot",
      x_accessor: "x",
      y_accessor: "y",
      chart_type:'point',
      //click_to_zoom_out: false,
      //brush: 'xy',
        mouseover: function(d, i) {
            // custom format the rollover text, show days
            d3.select('#data_plot svg .mg-active-datapoint')
                .text(d.data.filename);
        },
    });
    var voronoi_cells = d3.selectAll('.mg-voronoi path');
    voronoi_cells.on('click', function(d) {
        //console.log(d.data)
        copyToClipboard(d.data.filename)
        document.getElementById("selected_display").innerText = d.data.filename
    });
    //voronoi_cells.on('mouseover', function(d) {
    //    console.log(d)
        //add_filename_data(d.data.filename)
    //});
    $('#play_input_el').bind('input', function() {
        var this_val = $(this).val() // get the current value of the input field.
        if(filename_set.has(this_val)){
            add_audio_player(this_val)
        }
    });
    var filename_list = input_json_data.map(dict=>dict['filename'])
    console.log(filename_list)
    add_to_dropdown_menu(document.getElementById("play_item"),filename_list)
}

//function make_download_button()
$(document).ready(function(e) {
    make_graphic()
})
