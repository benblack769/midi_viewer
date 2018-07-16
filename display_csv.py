import sklearn.manifold
import numpy as np
import pandas
#import matplotlib.pyplot as plt
import plotly.offline as py
import plotly.graph_objs as go

def calc_tsne(data):
    tsne = sklearn.manifold.TSNE()
    #print(data.shape)
    #exit(1)
    transformed_data = tsne.fit_transform(data)

    return transformed_data
    #print(data)


def associate_metadata(data_2d, associate_dataframe):
    xvals,yvals = np.transpose(data_2d)
    val_dataframe = pandas.DataFrame(data={"x":xvals,"y":yvals})
    associate_dataframe = pandas.concat([associate_dataframe.reset_index(),val_dataframe],axis=1)

    return associate_dataframe

def plot_associated_data_matplotlib(df):
    groups = df.groupby('major_minor')

    # Plot
    fig, ax = plt.subplots()
    ax.margins(0.05) # Optional, just adds 5% padding to the autoscaling
    for name, group in groups:
        ax.plot(group.x, group.y, marker='o', linestyle='', ms=5, label=name)
    ax.legend()

    plt.show()

def plot_associated_data(df):
    groups = df.groupby('key')

    # Plot
    traces = []
    for name, group in groups:
        trace = go.Scatter(
            x = group.x,
            y = group.y,
            mode = 'markers',
            name = name)
        traces.append(trace)

    layout= go.Layout(
        title= 'Musical thingies',
        hovermode= 'closest')

    fig = go.Figure(data=traces, layout=layout)

    py.plot(fig, filename='scatter-mode')


if __name__ == "__main__":
    base_path = "../midi_dataset/"
    data_path = base_path + "annotated_data.csv"
    weights_path = base_path + "weights.npy"

    weights = np.load(weights_path)
    associate = pandas.read_csv(data_path)
    print(associate)
    weights_2d = calc_tsne(weights)
    all_data = associate_metadata(weights_2d,associate)
    plot_associated_data(all_data)
