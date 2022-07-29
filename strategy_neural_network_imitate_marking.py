
# TODO : Try to force StrategyNeuralNetwork to imitate StrategyWithObjectives :
#           for all possible actions:
#               - the StrategyNeuralNetwork (trained to return the number of victory points) marks this action
#                 by doing it and rating the game state.
#               - the StrategyWithObjectives marks this action seeing it as an objective
#             (we are not necessarily doing it for evey single action...)
#           Now we have for each actions:
#               - the input vector corresponding
#               - the mark of the StrategyNeuralNetwork
#               - the mark of the StrategyWithObjectives
#            -> We now just have to scale these last marks by an affine relation for instance: we can for example
#               translate and scale up or down these marks in order to have the same mean and standard deviation
#               than the marks of the StrategyNeuralNetwork ! : Here we have the "answers" for backpropagation !!
#            (with this technic, we can't make a data base: the answers depend of the state of the neural network :( )
#        I think we could by doing so considerably increase the performance of the neural network player (witch are
#        quite pathetic for now !).
