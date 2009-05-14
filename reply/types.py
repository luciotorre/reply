
class Parameter(object):
    pass


class Number(Parameter):
    def __init__(self, min, max):
        self.min = min
        self.max = max


class Integer(Number):
    def __str__(self):
        return "(%i %i)" % (self.min, self.max)


class Double(Number):
    def __str__(self):
        return "(%f %f)" % (self.min, self.max)


class Char(Parameter):
    pass


class ListOf(Parameter):
    def __init__(self, num, type):
        self.num = num
        self.type = type


class Space(object):
    def __init__(self, spec, order=None):
        self.spec = spec
        self.order = order

        self.names, self.values = self._build()

    def _build(self):
        doubles = []
        chars = []
        ints = []
        spec = self.spec

        if self.order is None:
            order = sorted(self.spec.keys())
        else:
            order = self.order

        for key in order:
            value = spec[key]

            if isinstance(value, ListOf):
                type_ = value.type
            else:
                type_ = value

            if isinstance(type_, Double) :
                doubles.append((key, value))
            elif isinstance(type_, Integer):
                ints.append((key, value))
            elif isinstance(type_, Char):
                chars.append((key, value))

        charcount = sum([ x.num if isinstance(x, ListOf) else 1 for x in chars])
        names = []
        values = []
        if ints:
            values.append("INTS %s" % " ".join([ str(y) for (x, y) in ints]))
            names.append("INTS %s" % " ".join([ str(x) for (x, y) in ints]))
        if doubles:
            values.append("DOUBLES %s" %
                          " ".join([ str(y) for (x, y) in doubles]))
            names.append("DOUBLES %s" %
                         " ".join([ str(x) for (x, y) in doubles]))
        if chars:
            values.append("CHARCOUNT %s" % charcount)
        return (" ".join(names), " ".join(values))

    @classmethod
    def parse(cls, values):
        space = Space({})
        int_count = 0
        double_count = 0
        charcount_count = 0
        for i, val in enumerate(values):
            if val == 'INTS':
                int_count += 1
                ints = values[i+1] + ', ' + values[i+2]
                int_t = eval(ints)
                space.spec['int' + str(int_count)] = Integer(*int_t)
            elif val == 'DOUBLES':
                double_count += 1
                doubles = values[i+1] + ', ' + values[i+2]
                double_t = eval(doubles)
                space.spec['double' + str(double_count)] = Double(*double_t)
            elif val == 'CHARCOUNT':
                charcount = int(values[i+1])
                for j in xrange(1, charcount+1):
                    space.spec['char' + str(j)] = Char()

        return space


