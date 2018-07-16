function clicked_item(item){
    console.log(item)
    console.log("argg@!!!")
}
function make_graphic(){
    MG.data_graphic({
      title: "UFO Sightings",
      //description: "Yearly UFO sightings from 1945 to 2010.",
      data: input_json_data,
      width: 400,
      height: 250,
      target: "#data_plot",
      x_accessor: "x",
      y_accessor: "y",
      //mouseover: null,
      click: clicked_item,
      mouseover: function(d, i) {
        console.log("moused!")
      },
      chart_type:'point',
      click_to_zoom_out:false,
    });
}

//function make_download_button()
$(document).ready(function(e) {
    make_graphic()
})
