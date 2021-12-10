import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.crossword.variables:
            l=variable.length
            words=self.domains[variable].copy()
            for word in words:
                if len(word)!=l:
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised=False

        x_domain=self.domains[x].copy()
        y_domain=self.domains[y]

        if x.length==y.length:
            for word in x_domain:
                if not y_domain-{word}:
                    self.domains[x].remove(word)
                    revised=True

        overlap=self.crossword.overlaps[x,y]
        if overlap:
            i,j=overlap
            x_d=set()
            for word_1 in x_domain:
                for word_2 in y_domain:
                    if word_1[i]==word_2:
                        x_d.add(word_1)
                        revised=True
                        break

        self.domains[x]=x_d
        return(revised)

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs==None:
            arcs=[]
            for variable in self.crossword.variables:
                neighbors=self.crossword.neighbors(variable)
                for neighbor in neighbors:
                    arcs.append((variable, neighbor))

        else:
            while len(arcs)!=0:
                x,y=arcs.pop()
                if revise(self,x,y):
                    if len(self.domains[x])==0:
                        return False
                    for neighbor in self.crossword.neighbors(x)-y:
                        arcs.append(x,neighbor)
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment)==0:
            return False

        for variable in self.crossword.variables:
            if variable in assignment:
                if assignment[variable]==None:
                    return False
            else:
                return False

        return True


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        words=assignment.values()
        if len(words)!=len(set(words)):
            return False

        for variable in assignment:
            if variable.length!=len(assignment[variable]):
                return False

        for variable in assignment:
            for neighbor in self.crossword.neighbors(variable):
                if neighbor in assignment.keys():
                    if self.crossword.overlaps[variable,neighbor]:
                        i,j=self.crossword.overlaps[variable,neighbor]
                        if assignment[variable][i]!=assignment[neighbor][j]:
                            return False
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        rating=[]
        neighbors=self.crossword.neighbors(var)

        for word in self.domains[var]:
            n=0
            for neighbor in neighbors:
                if neighbor not in assignment:
                    overlap=self.overlaps[word,neighbor]
                    if overlap!= None:
                        for word2 in self.domains[neighbor]:
                            if word[overlap[0]]!=word2[overlap[1]]:
                                n+=1
            rating.append((n,word))

        rating=sorted(rating)
        domain=[i[1] for i in rating]
        return domain


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        rating=[]
        for var in self.crossword.variables:
            if var not in assignment:
                domain=len(self.domains[var])
                rating.append((domain,var))

        rating=sorted(rating,key=lambda n:rating[0])

        degree=[]
        if len(rating)>1:
            if rating[0][0]==rating[1][0]:
                degree.append((len(self.crossword.neighbors(rating[0][1])),rating[0][1] ) )
                degree.append((len(self.crossword.neighbors(rating[1][1])),rating[1][1] ) )

                degree=sorted(degree,key=lambda x:degree[0] ,reverse=True)
                return(degree[0][1])
            else:
                return(rating[0][1])
        else:
            return(rating[0][1])


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var=self.select_unassigned_variable(assignment)
        for word in self.domains[var]:
            assignment[var]=word
            if self.consistent(assignment):
                assignment[var]=word
                result=self.backtrack(assignment)

                if result != None:
                    return result

                assignment.pop(var,None)

        return None





def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
