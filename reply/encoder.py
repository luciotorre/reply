import numpy

class Encoder(object):
    def __init__(self, rl):
        """
        state_space is a list of dimensions where each one has the list of posible
        values for that dimension. A world encoded representation of a state
        is a list with one value picked from each dimension.

        action_space is a list of dimensions where each one has the list of posible
        values for that dimension. A world encoded representation of an action
        is a list with one value picked from each dimension.
        """
        self.rl = rl
        self.state_space = self.rl.get_state_space()
        self.action_space = self.rl.get_action_space()
        
    def new_episode(self):
        pass
    def end_episode(self):
        pass
    
    def encode_state(self, state):
        """
        The parameters are received in world-encoding and returned
        in rl-encoding
        """    
        raise NotImplementedError()
        
    def encode_action(self, action):
        """
        The parameters are received in world-encoding and returned
        in rl-encoding
        """
        raise NotImplementedError()
        
    def decode_action(self, action_n):
        """
        The parameters are received in rl-encoding and returned
        in world-encoding
        """    
        raise NotImplementedError()
        
class DistanceEncoder(Encoder):
    def get_space_size(self, space):
        pz = 1
        for dim in space:
            pz *= len(dim)
        return pz
        
    def __init__(self, rl):
        super(DistanceEncoder, self).__init__(rl)
        self.input_size = self.get_space_size(self.state_space)
        self.output_size = self.get_space_size(self.action_space)
        
    def encode_state(self, state):
        """
        do base convertion from variable-base state to 10-based state number
        """
        state = [ state[dim.name] for dim in self.state_space]
            
        m = 1
        state_n = 0
        for dim, v in zip(self.state_space, state):
            n = numpy.argmin( (dim.points-v)**2 )
            state_n += n*m
            m *= len(dim)
        return state_n
        
    def encode_action(self, action):
        """
        do base conversion from variable-base action to 10-base action number
        """
        m = 1
        action_n = 0
        for dim, v in zip(self.action_space, action):
            n = numpy.argmin( (dim.points-v)**2 )
            action_n += n*m
            m *= len(dim)
        return action_n
        
    def decode_action(self, action_n):
        """
        do base conversion from 10-base action number to variable-base
        action
        """
        m = 1

        action = numpy.zeros( len(self.action_space) )
        for i, dim in enumerate(self.action_space):
            n = len(dim)
            j = ( action_n/m ) % n
            m *= n
            action[i] = dim.points[j]
            #print n, j, m, dim[j], dim
        return action

if __name__=="__main__":
    import rl
    en = DistanceEncoder( 
        [ rl.dimension(0,3,4) ],
        [ rl.dimension(0,3,4) ] 
        )
    for i in range(4):
        print i, "-->", en.encode_state( [i] )
        
    print "--"*20
    en = DistanceEncoder( 
        [ rl.dimension(0,3,4), rl.dimension(0,5,6) ],
        [ rl.dimension(0,3,4) ] 
        )
    for i in range(4):
        for j in range(6):
            print i,j, "-->", en.encode_state( (i, j) )
