var filename_set = new Set(input_json_data.map(dict=>dict.filename))

function make_dropdown_menu(){
    if(input_json_data.length == 0){
        return;
    }
    var object = Object.assign({},input_json_data[0]);
    delete object.x;
    delete object.y;
    delete object.filename;

    var keys = Object.keys(object);
    console.log(keys)
    add_to_dropdown_menu(document.getElementById("category_options"),keys)
}
function unique_items(data_list,key){
    console.log(data_list)
    console.log(Array.from(new Set(data_list.map(d=>d[key]))))
    return Array.from(new Set(data_list.map(d=>d[key])))
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
function downloadURI(uri, name) {
    var link = document.createElement("a");
    link.download = name;
    link.href = uri;
    link.type = "audio/mid"
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    delete link;
}

function make_graphic(){
    var selected = $("#category_options").val();
    console.log(selected)
    MG.data_graphic({
      title: "Musica",
      description: "Click to copy point filenames to ",
      width: 800,
      height: 600,
      data:input_json_data,
      target: "#data_plot",
      x_accessor: "x",
      y_accessor: "y",
        color_accessor: selected,
        color_type:'category',
      chart_type:'point',
        //legend: ['arg','var'],
      //click_to_zoom_out: false,
      //brush: 'xy',
    });

    var voronoi_cells = d3.selectAll('.mg-voronoi path');
    voronoi_cells.on('click', function(d) {
        //console.log(d.data)
        //copyToClipboard(d.data.filename)
        document.getElementById("selected_display").innerText = d.data.filename
    });
}
function setup_interactive(){
    var filename_list = input_json_data.map(dict=>dict['filename'])

    $("#category_options").change(make_graphic)
    function download_type(folder){
        var this_val = document.getElementById("selected_display").innerText;
        if(filename_set.has(this_val)) {
            MIDIjs.play(folder+this_val)
        }
    }
    $("#orig_download").click(function(){
        download_type("midi_files/")
    })
    $("#manip_download").click(function(){
        download_type("midi_text_midi_files/")
    })
}
//function make_download_button()
$(document).ready(function(e) {
    make_dropdown_menu()
    setup_interactive()
    make_graphic()
})
