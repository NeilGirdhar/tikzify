__all__ = ['EDGE_COLORS', 'PALETTE']


EDGE_COLORS = {prefix + edge_name: color
               for color, edges in [('dcolorb', ['explanation', 'prediction']),
                                    ('dcoloro', ['demand', 'waking', 'selection']),
                                    ('dcolorr', ['pooling']),
                                    ('dcolorg', ['gln'])]
               for edge_name in edges
               for prefix in ['', 'co_']}


PALETTE = [('dcolorb', 'dhcolorb'),
           ('dcoloro', 'dhcoloro'),
           ('dcolorr', 'dhcolorr'),
           ('dcolorg', 'dhcolorg'),
           ('dcolorbrown', 'dhcolorbrown'),
           ('dcolory', 'dhcolory')]
