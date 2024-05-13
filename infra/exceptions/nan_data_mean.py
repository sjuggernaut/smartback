class DataMeanNanException(Exception):
    def __init__(self, session, *args):
        super().__init__(args)
        self.session = session

    def __str__(self):
        return f"The data mean for the session {self.session} is NaN which means data source is not providing good data. Please check the data source and try again. ]"
