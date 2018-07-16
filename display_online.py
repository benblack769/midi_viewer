import dash_dangerously_set_inner_html
import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import numpy as np
import pandas
import binascii
from display_csv import calc_tsne,associate_metadata

base_path = "../midi_dataset/"
data_path = base_path + "annotated_data.csv"
weights_path = base_path + "weights.npy"

weights = np.load(weights_path)
associate = pandas.read_csv(data_path)
weights_2d = calc_tsne(weights)
all_data = associate_metadata(weights_2d,associate)

def get_path_from_file(midi_filename,author):
    midi_path = base_path + author + "/" + midi_filename
    print(midi_path)
    return midi_path

def get_figure_data(df):
    groups = df.groupby('key')
    figure = []

    # Plot
    traces = []
    for name, group in groups:
        trace = {
            "x":group.x,
            "y":group.y,
            "text":group.key,
            "author":group.author,
            "music_key":group.key,
            "majorminor":group.majorminor,
            "filename":group.path,
            'name': name,
            'mode': 'markers'
        }
        traces.append(trace)

    return traces


app = dash.Dash('')

app.scripts.config.serve_locally =True

app.layout = html.Div([
    dcc.Graph(
        id='basic-interactions',
        figure={
            'data': get_figure_data(all_data),
            'layout':  go.Layout(
                hovermode='closest'
            ),
        }
    ),
    html.Div([
        dash_dangerously_set_inner_html.DangerouslySetInnerHTML("<button></button>"),
    ],id='click-data')
])

@app.callback(
    Output('click-data', 'children'),
    [Input('basic-interactions', 'clickData')])
def display_hover_data(clickData):
    print(clickData)
    pointdata = clickData['points'][0]
    index = pointdata['pointIndex']
    midi_filename = all_data['path'][index]
    author = all_data['author'][index]
    path = get_path_from_file(midi_filename,author)
    bin_data = open(path,'rb').read()
    data = binascii.hexlify(bin_data)
    #print(bin_data)
    print(data)

    html_data = '''
    <button onclick="
    var data='%s'
    var filename='%s'
    var typedArray = new Uint8Array(data.match(/[\da-f]{2}/gi).map(function (h) {
      return parseInt(h, 16)
    }))
    var blob = new Blob([typedArray],{type:'application/octet-stream'})
    if(window.navigator.msSaveOrOpenBlob) {
        window.navigator.msSaveBlob(blob, filename);
    }
    else{
        var elem = window.document.createElement('a');
        elem.href = window.URL.createObjectURL(blob);
        elem.download = filename;
        document.body.appendChild(elem);
        elem.click();
        document.body.removeChild(elem);
    }">Download %s</button>
    ''' % (data,midi_filename,midi_filename)
    print(html_data)
    #argdata = "<button>{}</button>".format(clickData)
    return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(html_data)
    #return json.dumps(hoverData, indent=2)

#click_data = {u'points': [{u'curveNumber': 1, u'text': u'Ab', u'pointNumber': 2, u'pointIndex': 2, u'y': -4.351526260375977, u'x': 4.2963337898254395}]}
#display_hover_data(click_data)
#exit(0)

if __name__ == '__main__':
    app.run_server(debug=True)#,host="0.0.0.0")
