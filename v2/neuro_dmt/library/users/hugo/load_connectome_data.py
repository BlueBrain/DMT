def load_connectome_data(filename):
    from dmt.tk.collections.dataframes import FODict

    def column_to_FODict(col):
        return [FODict(eval(string[20:-2])) for string in col]

    frame = pd.read_csv(filename, index_col=0)
    frame.presynaptic = column_to_FODict(frame.presynaptic)
    frame.postsynaptic = column_to_FODict(frame.postsynaptic)
    return frame
