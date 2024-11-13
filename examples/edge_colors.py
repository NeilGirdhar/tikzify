__all__ = ['EDGE_COLORS', 'PALETTE']


EDGE_COLORS = {prefix + edge_name: color
               for color, edges in [('dcolorb', ['gln', 'explanation', 'deduction']),
                                    ('dcoloro', ['variational', 'pooling', 'geminate',
                                                 'attention']),
                                    ('dcolorr', ['recognition']),
                                    ('dcolorg', ['control'])]
               for edge_name in edges
               for prefix in ['', 'co_']}


PALETTE: list[tuple[str, str]] = [('dcolorb', 'dhcolorb'),
                                  ('dcoloro', 'dhcoloro'),
                                  ('dcolorr', 'dhcolorr'),
                                  ('dcolorg', 'dhcolorg'),
                                  ('dcolorbrown', 'dhcolorbrown'),
                                  ('dcolory', 'dhcolory')]
