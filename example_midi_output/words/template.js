var word_mapping = new Map(input_json_data.map(dict=>[dict.chord_repr,dict]))
//input_json_data.forEach(function(dict){word_mapping[dict.chord_repr]=dict})
var word_list = input_json_data.map(dict=>dict.chord_repr)

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
function play_audio(source_name){
    var ogg_path = "midi_ogg_files/"+source_name+".ogg"
    document.getElementById("player_source").src = ogg_path
    var player = document.getElementById("audio_player")
    //player.play();
    player.addEventListener('loadeddata', function() {
      if(player.readyState >= 2) {
        player.play();
      }
  });
  player.load();
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
    var voronoi_cells = d3.selectAll('.mg-voronoi path');
    voronoi_cells.on('click', function(d) {
        //console.log(d.data)
        copyToClipboard(d.data.chord_repr)
        play_audio(d.data.chord)
        document.getElementById("selected_display").innerText = d.data.chord_repr
    });
    $('#play_input_el').bind('input', function() {
        var this_val = $(this).val() // get the current value of the input field.
        if(word_mapping.has(this_val)){
            play_audio(word_mapping.get(this_val).chord)
        }
    });
    $("#play_button").click(function(){
        var this_val = $('#play_input_el').val() // get the current value of the input field.
        if(word_mapping.has(this_val)){
            play_audio(word_mapping.get(this_val).chord)
        }
    })
    add_to_dropdown_menu(document.getElementById("play_item"),word_list)
}

//function make_download_button()
$(document).ready(function(e) {
    make_graphic()
})
