from pyxlsb2.records import FormulaCellRecord

from .tokenreader import TokenReader

import logging

_logger = logging.getLogger(__name__)

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
        formula = '' if not tokens else tokens.pop().stringify(tokens, workbook)
        if formula is not None:
            formula = formula.strip()
        _logger.debug("Formula: %s" % formula)
        return formula

    @classmethod
    def parse(cls, data, anchor_row=None, anchor_col=None):
        if anchor_row is not None: Formula.anchor_row = anchor_row
        if anchor_col is not None: Formula.anchor_col = anchor_col
        _logger.debug("Parsing formula at row=%s col=%s data=%s" % (anchor_row, anchor_col, data))
        return cls(TokenReader(data))
