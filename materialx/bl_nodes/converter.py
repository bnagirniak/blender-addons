# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

from .node_parser import NodeParser
from . import log


class ShaderNodeMath(NodeParser):
    """ Map Blender operations to MaterialX definitions, see the stdlib_defs.mtlx in MaterialX """

    def export(self):
        op = self.node.operation
        in1 = self.get_input_value(0)
        # single operand operations
        if op == 'SINE':
            res = in1.sin()
        elif op == 'COSINE':
            res = in1.cos()
        elif op == 'TANGENT':
            res = in1.tan()
        elif op == 'ARCSINE':
            res = in1.asin()
        elif op == 'ARCCOSINE':
            res = in1.acos()
        elif op == 'ARCTANGENT':
            res = in1.atan()
        elif op == 'LOGARITHM':
            res = in1.log()
        elif op == 'ABSOLUTE':
            res = abs(in1)
        elif op == 'FLOOR':
            res = in1.floor()
        elif op == 'FRACT':
            res = in1 % 1.0
        elif op == 'CEIL':
            res = in1.ceil()
        elif op == 'ROUND':
            f = in1.floor()
            res = (in1 % 1.0).if_else('>=', 0.5, f + 1.0, f)

        else:  # 2-operand operations
            in2 = self.get_input_value(1)

            if op == 'ADD':
                res = in1 + in2
            elif op == 'SUBTRACT':
                res = in1 - in2
            elif op == 'MULTIPLY':
                res = in1 * in2
            elif op == 'DIVIDE':
                res = in1 / in2
            elif op == 'POWER':
                res = in1 ** in2
            elif op == 'MINIMUM':
                res = in1.min(in2)
            elif op == 'MAXIMUM':
                res = in1.max(in2)

            else:
                in3 = self.get_input_value(2)

                if op == 'MULTIPLY_ADD':
                    res = in1 * in2 + in3
                else:
                    log.warn("Unsupported math operation", op)
                    return None

        if self.node.use_clamp:
            res = res.clamp()

        return res
