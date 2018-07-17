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
      click_to_zoom_out: false,
    });
    d3.selectAll('path').on('click', function(d, i,arg) {
        console.log(d.data)
        copyToClipboard(d.data.filename)
    });
    var filename_list = input_json_data.map(dict=>dict['filename'])
    console.log(filename_list)
    add_to_dropdown_menu(document.getElementById("play_item"),filename_list)
}

//function make_download_button()
$(document).ready(function(e) {
    make_graphic()
})
