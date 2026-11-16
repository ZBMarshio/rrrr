class JointLog:
    def __init__(self, name):
        self.name = name
        self.samples = []

    def add(self, position_rad):
        self.samples.append(position_rad)

log = JointLog("left_joint")
alias = log
other = JointLog("right_joint")
alias.add(0.2)
other.add(-0.1)
print(log.name, log.samples)
print(other.name, other.samples)
