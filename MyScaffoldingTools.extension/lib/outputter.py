from pyrevit import output

class Outputter(object):
    def __init__(self):
        self.out = output.get_output()

    def __getattr__(self, name):
        return getattr(self.out, name)
    
    def print_response(self, check_name, response, color="black"):
        """Prints a formatted response where check name is bolded text and the response is text with given color.

        Args:
            check_name (str): _description_
            response (str): _description_
            color (str, optional): Text color for the response. Defaults to "black".
        """

        self.out.print_html("<p><b>{0}:</b> <span style='color:{1};'>{2}</span></p>".format(check_name, color, response))
    
    def print_score_summary(self, summary_name, score, score_header="Score"):
        points, checks, percentage = score
        self.out.print_md("### <u>{0}: Points gained {1} out of {2}. {4}: {3}</u>".format(summary_name, points, checks, percentage, score_header))

    def print_pie_chart(self, points, checks):
        """
        Prints a pie chart to represent points and missed checks.

        Args:
            points (int): Number of points scored.
            checks (int): Total number of checks.
        """

        chart = self.out.make_pie_chart()
        chart.data.labels = ["Succeed", "Failed"]
        dataset = chart.data.new_dataset("Data")
        dataset.data = [points, checks - points]
        dataset.backgroundColor = ["green", "red"]
        chart.options.title = {"display": True, "text": "Project parameter summary", "fontStyle": "bold"}
        
        chart.draw()