from csp import *
import sys
import time

class kenken_puzzle(CSP):

    def __init__(self, file):

        # Read the contents of the txt file.
        with open(file, 'r') as f:
            # The first line states the size.
            size = int(f.readline())
            # The following lines are the kenken puzzle.
            puzzle = f.readlines()[0:]

        f.close()
        
        # Initialization of the csp parameters.
        self.variables = list()
        self.neighbors = dict()
        self.domains = dict()
        self.cages = dict()
        self.size = size
        self.constraint_counter = 0

        # Create the list of variables.
        for i in range(size):
            for j in range(size):
                self.variables.append((i,j))

        # Create the dictionary of the neighbors.
        for variable in self.variables:
            neighbor_dictionary_value = list()

            variable_x_coord = int(list(variable)[0])
            variable_y_coord = int(list(variable)[1])

            for i in range(size):
                if i != variable_y_coord:
                    neighbor_dictionary_value.append((variable_x_coord,i))
            for i in range(size):
                if i != variable_x_coord:
                    neighbor_dictionary_value.append((i,variable_y_coord))
        
            self.neighbors[variable] =  neighbor_dictionary_value


        # Create the dictionary of the domains.
        variable_values = list(range(1,self.size+1))
        for variable in self.variables:
            self.domains[variable] = variable_values

        # Create the dictionary of the constraints.
        for line in puzzle:

            cage_variables, cage_operator, cage_target = line.split()

            cage_variables_list = cage_variables.rsplit('-')

            # From list of strings to list of tuples (x,y)
            cage_variable_list_tuple = list()
            for variable in cage_variables_list:
                x = int(list(variable)[1])
                y = int(list(variable)[3])
                cage_variable_list_tuple.append((x,y))

            for variable in cage_variable_list_tuple:
                self.cages[variable] = (cage_variable_list_tuple, cage_operator, int(cage_target))

        CSP.__init__(self, self.variables, self.domains, self.neighbors, self.kenken_constraints)


    def kenken_constraints(self, A, a, B, b):

        # Increment the constraint checks counter.
        self.constraint_counter+=1

        # Check if any neighbor of A has already the value a.
        for var in self.neighbors[A]:
            if var in self.infer_assignment() and self.infer_assignment()[var] == a:
                return False
    
        # Check if any neighbor of B has already the value b.
        for var in self.neighbors[B]:
            if var in self.infer_assignment() and self.infer_assignment()[var] == b:
                return False

        # Check if B is a neighbor of A and they have the same value.
        if( B in self.neighbors[A] and a==b):
            return False

        # Check the constraints of the cage-operation.
        return self.constraint_check_operation(A, a, B, b)
        

    def constraint_check_operation(self, A, a, B, b):

        cage_variables, cage_operator, cage_target = list(self.cages[A])

        # Cage operation: No operation.
        if(cage_operator == '?'):
            return a == cage_target

        # Cage operation: Multiplication.
        elif(cage_operator == 'mult'):
            assigned = 1
            prod = a

            # Calculate the product of the cage variables.
            for var in cage_variables:
                if var!=A and var in self.infer_assignment():
                    prod *= self.infer_assignment()[var]
                    assigned +=1

            # Compare the number of assigned variable and the product of them.
            if assigned == len(cage_variables):
                return prod == cage_target 
            elif assigned < len(cage_variables):
                return prod <= cage_target
            else:
                return False

        # Cage operation: Addition.
        elif(cage_operator == 'add'):
            sum = a
            assigned = 1

            # Calculate the sum of the assigned cage variables.
            for var in cage_variables:
                if var!=A and var in self.infer_assignment():
                    sum += self.infer_assignment()[var]
                    assigned +=1
            
            # Compare the number of assigned variable and the sum of them.
            if assigned == len(cage_variables):
                return sum == cage_target 
            elif assigned < len(cage_variables):
                return sum < cage_target
            else:
                return False
        
        # Cage operation: Subtraction.
        elif(cage_operator == 'sub'):

            # Check if B is in the cage variables.
            if(B not in cage_variables):

                # If not find the second number.
                for var in cage_variables:
                    if(var!=A and var in self.infer_assignment()):
                        b = self.infer_assignment()[var]
                        return (max(a,b)-min(a,b)) == cage_target

            # If yes check if the subtraction is equal to the target
            else:
                return (max(a,b)-min(a,b)) == cage_target

        # Cage operation: Division.
        elif(cage_operator == 'div'):

            # Check if B is in the cage variables.
            if(B not in cage_variables):

                # If not find the second number.
                for var in cage_variables:
                    if(var!=A and var in self.infer_assignment()):
                        b = self.infer_assignment()[var]
                        return (max(a,b)/min(a,b)) == cage_target
            
            # If yes check if the subtraction is equal to the target
            else:
                return (max(a,b)/min(a,b)) == cage_target
        
        return True


    def display(self, assignment):
        for i in range(self.size):
            for j in range(self.size):
                sys.stdout.write(str(assignment[(i,j)]) + " ")
            print()

    def get_constraint_counter(self):
        return self.constraint_counter
    
    def get_assignments_counter(self):
        return self.nassigns

def kenken_solver(file, algorithm):

    kenken = kenken_puzzle(file)

    print("KenKen")

    start_time = time.clock()

    if(algorithm == "BT"):
        kenken.display(backtracking_search(csp=kenken))
    elif(algorithm == "BT+MRV"):
        kenken.display(backtracking_search(csp=kenken, select_unassigned_variable=mrv))
    elif(algorithm == "BT+LCV"):
        kenken.display(backtracking_search(csp=kenken, order_domain_values=lcv))
    elif(algorithm == "FC"):
        kenken.display(backtracking_search(csp=kenken, inference=forward_checking)) 
    elif(algorithm == "FC+MRV"):
        kenken.display(backtracking_search(csp=kenken, inference=forward_checking, select_unassigned_variable=mrv))
    elif(algorithm == "FC+LCV"):
        kenken.display(backtracking_search(csp=kenken, inference=forward_checking, order_domain_values=lcv))
    elif(algorithm == "MAC"):
        kenken.display(backtracking_search(csp=kenken, inference=mac))
    elif(algorithm == "MIN"):
        result = min_conflicts(csp=kenken)
        if(result == None):
            print("Minconficts could not find a solution.")
            quit()
        kenken.display(result)
    else:
        print("Error: Not existing <algorithm>.")
        quit()
    
    finish_time = time.clock()

    print("Time: " + str(finish_time-start_time))
    print("Total constraints checks: " + str(kenken.get_constraint_counter()))
    print("Total assignments: " + str(kenken.get_assignments_counter()))
    quit()

# Usage: python kenken.py <file> <algorithm>
# eg. <file> = ./puzzles/puzzle_3x3.txt
# <algorithm> = BT/BT+MRV/BT+LCV/FC/.../MAC/MIN

if __name__ == '__main__':

    if(len(sys.argv) != 3):
        print("Error: Usage: python kenken.py <file> <algorithm>.")
        quit()
    else:
        file = sys.argv[1]
        algorithm = sys.argv[2]

    kenken_solver(file,algorithm)

    
    
    
        


    

            
            

        



