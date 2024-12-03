# -*- coding: utf-8 -*-

class ScoreCounter:
    def __init__(self):
        self.points = 0
        self.checks = 0

    def increment_points(self, count=1):
        self.points += count

    def increment_checks(self, count=1):
        self.checks += count

    def get_points(self):
        return self.points
    
    def get_checks(self):
        return self.checks

    def get_score_percentage(self):
        """Calculate and return the score percentage as a string.

        Returns:
            str: Score percentage in string format.
        """

        if self.checks == 0:
            percentage = 0.0
        else:
            percentage = float((self.points) / float(self.checks)) * 100
        
        return self.points, self.checks, "{:.1f} %".format(percentage)

    def __add__(self, other):
        """Allow adding two ScoreCounter instances."""
        
        if not isinstance(other, ScoreCounter):
            return NotImplemented
        combined = ScoreCounter()
        combined.points = self.points + other.points
        combined.checks = self.checks + other.checks
        return combined
