from .tokenreader import TokenReader


class Formula(object):

    # since we don't want to pass the anchor_row and anchor_col all the way down
    # via the stringify interface (that would change a lot of stringify functions)
    # we have a choice - put the anchor_row and anchor_col into the workbook
    # or define global variables
    #
    # this is fine as long we don't have nested formula objects

    anchor_row=0
    anchor_col=0

    def __init__(self, tokens):
        self._tokens = list(tokens)

    def __repr__(self):
        return 'Formula({})'.format(self._tokens)

    def __str__(self):
        return self.stringify()

    def stringify(self, workbook):
        tokens = self._tokens[:]
        return '' if not tokens else tokens.pop().stringify(tokens, workbook)

    @classmethod
    def parse(cls, data, anchor_row=None, anchor_col=None):
        if anchor_row is not None: Formula.anchor_row = anchor_row
        if anchor_col is not None: Formula.anchor_col = anchor_col
        return cls(TokenReader(data))
