"""Storage classes."""
import numpy

class Storage(object):

    """Storage base class."""

    def __init__(self, rl):
        """Initialize the storage.

        Arguments:
        rl -- an instance of the agent

        """
        self.rl = rl

    def new_episode(self):
        """Start a new episode.
        
        Histories and traces should be cleared here.

        """
        pass
    
    def end_episode(self):
        """End the current episode."""
        pass

    def store_value(self, state, action, new_value):
        """Update the (state, action) -> value relationship.

        The parameters are received in rl-encoding.

        """
        raise NotImplementedError()

    def get_value(self, state, action):
        """Return the value of the (state, action) pair.

        The parameters are received in rl-encoding.

        """
        raise NotImplementedError()

    def get_state_values(self, state):
        """Return an array of the action values for the given state.

        The parameters are received in rl-encoding.

        """
        raise NotImplementedError()

    def get_max_value(self, state):
        """Return the maximum action value for the given state.

        The parameters are received in rl-encoding.

        """
        raise NotImplementedError()


class TableStorage(Storage):

    """Storage that uses a table for its data."""

    def __init__(self, rl):
        """Initialize the storage.

        Arguments:
        rl -- an instance of the agent

        """
        super(TableStorage, self).__init__(rl)
        encoder = rl.encoder
        mappings = getattr(rl, "storage_mappings", None)
        if mappings is not None:
            self.state = numpy.zeros((encoder.input_size, encoder.output_size))
            for state, action in mappings.items():
                encoded_state = encoder.encode_state( state )
                self.state[encoded_state, action] = 1
        else:
            #self.state = numpy.random.random(
            #    (encoder.input_size, encoder.output_size))
            self.state = numpy.zeros((encoder.input_size, encoder.output_size))

    def store_value(self, state, action, new_value):
        """Update the (state, action) -> value relationship."""
        self.state[state, action] = new_value

    def get_value(self, state, action):
        """Return the value for the (state, action) pair."""
        return self.state[state, action]

    def get_max_value(self, state):
        """Return the maximum action value for the given state."""
        return max(self.state[ state ])

    def get_state_values(self, state):
        """Return an array of the action values for the given state."""
        return self.state[ state ]


class DebugTableStorage(TableStorage):

    """Storage that uses a table for its data, and has debugging 
    information.
    
    """

    @property
    def median_hits(self):
        """Return the median number of times the current state has been
        visited.

        """
        return numpy.median(self.debug_state)

    @property
    def count_hits(self):
        """Return the total number of times the current state has been
        visited.

        """
        return numpy.sum(self.debug_state)

    def __init__(self, rl):
        """Initialize the storage.

        Arguments:
        rl -- an instance of the agent

        """
        super(DebugTableStorage, self).__init__(rl)
        encoder = rl.encoder
        self.debug_state = numpy.zeros((encoder.input_size,
                                        encoder.output_size))

    def store_value(self, state, action, new_value):
        """Update the (state, action) -> value relationship."""
        self.value_change += abs(new_value-self.state[state, action])
        super(DebugTableStorage, self).store_value(state, action, new_value)
        self.sum_state_action_visits += self.debug_state[state, action]
        self.sum_state_visits += sum(self.debug_state[state])
        if sum(self.debug_state[state]) == 0:
            self.new_state_visits += 1
        if self.debug_state[state, action] == 0:
            self.new_state_action_visits += 1
        self.total_visits += 1
        self.debug_state[state, action] += 1

    def print_report(self):
        """Print out debugging information."""
        shape = self.debug_state.shape
        print "Dimension usage variation"
        print "Dimension usage median"
        print "Dimension usage average"
        print "Dimension coverage"
        print "State Coverage", \
            len(numpy.nonzero(numpy.sum(self.debug_state,1)))/float(shape[0])
        #print self.debug_state
        print "State Coverage median", \
            numpy.median(numpy.sum(self.debug_state, 1))
        sz = shape[0]*shape[1]
        print "State-Action Coverage", \
            len(numpy.nonzero(self.debug_state.reshape(sz)))/float(sz)
        print "State-Action Coverage median", \
            numpy.median(numpy.median(self.debug_state))
        print "new states visited:", \
            self.new_state_visits, \
            "%0.2f%%" % (100*self.new_state_visits/float(self.total_visits))
        print "new actions taken:", \
            self.new_state_action_visits, \
            "%0.2f%%" % (100*self.new_state_action_visits/ \
                         float(self.total_visits))
        print "sum state visit", \
            self.sum_state_visits, \
            "%0.2f" % (self.sum_state_visits/self.total_visits)
        print "sum state action visit", \
            self.sum_state_action_visits, \
            "%0.2f" % (self.sum_state_action_visits/self.total_visits)
        print "value change", \
            self.value_change, self.value_change/float(self.total_visits)

    def new_episode(self):
        """Start a new episode."""
        super(DebugTableStorage, self).new_episode()
        self.new_state_visits = 0
        self.sum_state_visits = 0
        self.new_state_action_visits = 0
        self.sum_state_action_visits = 0
        self.total_visits = 0
        self.value_change = 0

