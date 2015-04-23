__all__ = ['EDGE_COLORS', 'PALETTE']


EDGE_COLORS = {
    prefix + y + suffix: x
    for x, ys in [
        ('color_blue', ['explanation',
                        'deduction']),
        ('color_orange', ['demand']),
        ('color_red', ['pooling',
                       'ipooling',
                       'onset',
                       'forgetting']),
        ('color_green', ['intention',
                         'realization',
                         'boosting',
                         'regret']),
    ]
    for prefix in ['', 'g']
    for y in ys
    for suffix in ['', '_in']}


PALETTE = [
    ('color_blue', 'h_color_blue'),
    ('color_orange', 'h_color_orange'),
    ('color_red', 'h_color_red'),
    ('color_green', 'h_color_green'),
    ('color_brown', 'h_color_brown'),
    ('color_yellow', 'h_color_yellow')]
