from pyxlsb2.records import FormulaCellRecord

from .tokenreader import TokenReader
from .ptgs import UnknownPtg

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

    def __init__(self, tokens, parse_error=None):
        self._tokens = tokens
        self.parse_error = parse_error

    def __repr__(self):
        return 'Formula({})'.format(self._tokens)

    def __str__(self):
        return self.stringify()

    def stringify(self, workbook):
        if self.parse_error is not None:
            return "PARSE_ERROR: %s" % self.parse_error
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

        tokens = list(TokenReader(data))

        parse_error = None
        for token in tokens:
            if isinstance(token, UnknownPtg):
                _logger.warning("Parsing formula at row=%s col=%s data=%s resulted in UnknownPtg's")
                parse_error = "Unknown tokens found when parsing formula"
                break

        if parse_error is not None:
            count = 0
            for token in tokens:
                count += 1
                _logger.warning("%02d: %s" % (count, token))

        return cls(tokens, parse_error=parse_error)
