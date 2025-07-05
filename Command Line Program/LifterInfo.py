class LifterInfo:

    def __init__(self, name, link, squat_kg, bench_kg, deadlift_kg, total, dotscore, division):
        self.name = name
        self.link = link
        self.squat_kg = squat_kg
        self.bench_kg = bench_kg 
        self.deadlift_kg = deadlift_kg
        self.dotscore = dotscore
        self.total = total
        self.division = division
        

         # Convert to lbs with error handling
        try:
            self.squat_lbs = str(float(self.squat_kg) * 2.2046)
        except ValueError:
            self.squat_lbs = '0'

        try:
            self.bench_lbs = str(float(self.bench_kg) * 2.2046)
        except ValueError:
            self.bench_lbs = '0'

        try:
            self.deadlift_lbs = str(float(self.deadlift_kg) * 2.2046)
        except ValueError:
            self.deadlift_lbs = '0'

    #Overide the print statement
    def __str__(self):
        return (f"Name: {self.name} || Link: {self.link} || "
                f"Squat: {self.squat_lbs:.1f} lbs || Bench: {self.bench_lbs:.1f} lbs || Deadlift: {self.deadlift_lbs:.1f} lbs ||Total: {self.total} kgs ||DOTSCORE: {self.dotscore}" )

    
