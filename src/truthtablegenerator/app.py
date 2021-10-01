"""
A cross-platform Truth Table Generator written in Python.
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from inspect import signature

class Infix(object):
    def __init__(self, func):
        self.func = func
    def __or__(self, other):
        return self.func(other)
    def __ror__(self, other):
        return Infix(lambda x: self.func(other, x))
    def __call__(self, v1, v2):
        return self.func(v1, v2)

#         ~   ¬     ^   ⊕     &    ∧     |    ∨
t_dict = {38: 8743, 94: 8853, 124: 8744, 126: 172} # Dict for str.translate()
prettify = lambda s: s.translate(t_dict).replace('<->','↔').replace('->','→')

cond = Infix(lambda a,b: ~a | b) # Conditional
bicond = Infix(lambda a,b: ~(a ^ b)) # Biconditional
fix_inline = lambda s: s.replace('<->','|bicond|').replace('->','|cond|')

flatten = lambda l: sum(map(flatten,l),[]) if isinstance(l,list) else [l] # Flattens lists
get_arity = lambda f: len(signature(f).parameters) # Returns Arity of a Function
get_bits = lambda n: [*map(lambda x:[*map(int,bin(x)[2:].zfill(n))],range(2**n))] # Get Bits
gbfa = lambda f: get_bits(get_arity(f)) # Get Bits from Arity
output = lambda f: [*map(f,*zip(*gbfa(f)))] # Output of Boolean Function
make_tt = lambda f: [*map(flatten,[*map(list,zip(gbfa(f),output(f)))])] # Make Truth Table
gv = lambda s: sorted([*{*filter(str.isalpha,s)}]) # Gets Variables from String
gvf = lambda s: ','.join(gv(s)) # Get Vars (formatted)
mttfs = lambda s: make_tt(eval(f"lambda {gvf(s)}:[0,1][{fix_inline(s)}]")) # Make Truth Table from String
get_headings = lambda s: [*gv(s),prettify(s)]


class TruthTableGenerator(toga.App):

    def startup(self):
        self.main_box = toga.Box(style=Pack(direction=COLUMN))

        default_expression = "p -> q"

        input_label = toga.Label(
            'Enter a Boolean Expression: ',
            style=Pack(padding=(0, 5))
        )
        self.be_input = toga.TextInput(style=Pack(flex=1), placeholder=default_expression)

        input_box = toga.Box(style=Pack(direction=ROW, padding=5))
        input_box.add(input_label)
        input_box.add(self.be_input)

        button = toga.Button(
            'Generate Truth Table',
            on_press=self.make_tt,
            style=Pack(padding=5)
        )

        truth_table = toga.Table(headings=get_headings(default_expression), data=mttfs(default_expression))

        self.main_box.add(input_box)
        self.main_box.add(button)
        self.main_box.add(truth_table)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()

    def make_tt(self, widget):
        boolean_expression = self.be_input.value or 'p -> q'
        truth_table = toga.Table(headings=get_headings(boolean_expression), data=mttfs(boolean_expression))
        self.main_box.remove(self.main_box.children[-1])
        self.main_box.add(truth_table)
        

def main():
    return TruthTableGenerator() 
