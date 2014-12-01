class Maurice():

    def __init__(self):
        self.__name = "Roger"
        self.__prenom = "Maurice"
        self.__age = "48"

    def getAge(self):
        return self.__age

    def getName(self):
        return self.__name

    def getSurname(self):
        return self.__prenom

if __name__ is "__main__":
    m = Maurice()
    import pdb; pdb.set_trace()  # XXX BREAKPOINT
    print "{}, {} , {}".format(m.getName(), m.getSurname(), m.getName())
