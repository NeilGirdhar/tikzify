from edge_colors import EDGE_COLORS

from tikzify import NodeGraph, angles, default_waypoint_names, tex_file, tex_pic

dimmed_opacity = 0.18
iosize = r'\footnotesize '


def opacity(groups):
    return (1.0
            if opaque_group in groups or opaque_group == 'all'
            else dimmed_opacity)


with tex_file('basal_ganglia.tex',
              ['latex/includes',
               'latex/commands',
               'tikz/base',
               'tikz/colors',
               'tikz/extra_tips',
               'tikz/cmm_tips',
               'tikz/flow_style']) as f:
    for opaque_group in ['all',
                         # 'strp',
                         'strm',
                         'stn',
                         ]:
        network = NodeGraph(edge_colors=EDGE_COLORS)
        g = network.digraph
        with tex_pic(f,
                     'basal_ganglia-' + opaque_group,
                     'Flow diagram, /CMM tips'):
            D = default_waypoint_names()
            g.add_node('str_center', coordinate=True)
            mx, my = 4.5, 2.5
            px, py = 3.2, -0.0
            for name, x, y in [('strmi', -mx, my),
                               ('strmd', mx, my),
                               ('strpi', -px, py),
                               ('strpd', px, py)]:
                g.add_node(name,
                           state='big_circle',
                           relpos=(x, y, NodeAnchor('str_center')),
                           text=rf'$\{name}$')
            g.add_node('striatum_stretch',
                       coordinate=True,
                       relpos=(0.6, 0, RelativeAnchor('strmd', 'east')))
            g.add_node('sncd',
                       text=r'$\sncd$',
                       state='big_circle',
                       relpos=(0, -2.7, NodeAnchor('str_center')))
            g.add_node('sncv',
                       text=r'$\sncv$',
                       state='big_circle',
                       relpos=(2.0, 0, NodeAnchor('sncd')))
            g.add_node('gpen',
                       state='big_circle',
                       inner_sep='-3pt',
                       relpos=(-2.0, 0, NodeAnchor('sncd')),
                       text=r'$\gpen$')
            g.add_node('gpi_center',
                       coordinate=True,
                       relpos=(0, -2.0, NodeAnchor('sncd')))
            g.add_node('gpi',
                       state='big_circle',
                       relpos=(px, 0, NodeAnchor('gpi_center')),
                       text=r'$\gpi$')
            g.add_node('gpep',
                       state='big_circle',
                       inner_sep='-3.5pt',
                       relpos=(-px, 0, NodeAnchor('gpi_center')),
                       text=r'$\gpep$')
            g.add_node('stn',
                       state='big_circle',
                       relpos=(0, -3.3, NodeAnchor('sncd')),
                       text=r'$\stn$')
            for c, s in (('ctxpt', 'strmd'), ('ctxit', 'strmi')):
                x = (1 if c == 'ctxpt' else -1) * 1.0
                g.add_node(c,
                           state='coordinate',
                           relpos=(x, 5.9, NodeAnchor('str_center')),
                           text=iosize + rf'$\{c}$')
            g.add_node('below_stn',
                       coordinate=True,
                       relpos=(0.0, -0.4,
                               RelativeAnchor('stn', 'south')))
            g.add_node('reward',
                       state='coordinate',
                       pos=IntersectionAnchor('below_sncv1',
                                                  'below_stn'),
                       text=iosize + 'reward')
            g.add_node('thf',
                       state='coordinate',
                       pos=IntersectionAnchor('gpep', 'below_stn'),
                       text=iosize + 'desire (out)')
            g.add_node('tha',
                       state='coordinate',
                       pos=IntersectionAnchor('gpi', 'below_stn'),
                       text=iosize + 'fear (out)')
            for name, text, group in [
                    ('striatum', 'Striatum',
                     [f'str{b}{a}'
                      for a in 'di'
                      for b in 'mp']),
                    ('strp', 'Striatal patch',
                     [f'strp{a}'
                      for a in 'di']),
                    ('strm', 'Striatal matrix',
                     [f'strm{a}'
                      for a in 'di']),
                    # ('snc', 'SNc', ['sncd', 'sncv']),
            ]:
                g.add_node(name,
                           fit=group,
                           inner_sep=f"{12 if name=='striatum' else 5}mm",
                           state='rectangle, draw',
                           col='color_red',
                           dash='dashed',
                           corner={'text': iosize + text})
                for tract in ['ctxpt', 'ctxit', 'gpen',
                              'sncd', 'sncd0', 'sncd1', 'sncd2']:
                    g.add_node(f'{name}_{tract}',
                               coordinate=True,
                               pos=IntersectionAnchor(
                                   tract,
                                   RelativeAnchor(name,
                                                    ('north'
                                                     if tract in ['ctxpt', 'ctxit']
                                                     else 'south'))))
            g.add_node('left_of_everything',
                       coordinate=True,
                       relpos=(-0.3, 0,
                               RelativeAnchor('striatum', 'west')))
            g.add_node('right_of_everything',
                       coordinate=True,
                       relpos=(0.3, 0,
                               RelativeAnchor('striatum', 'east')))
            g.add_node('str_above',
                       coordinate=True,
                       relpos=(0, 0.3,
                               RelativeAnchor('striatum', 'north')))
            g.add_node('str_below',
                       coordinate=True,
                       relpos=(0, -0.3,
                               RelativeAnchor('striatum', 'south')))
            for i, j in angles(180, 3):
                g.add_node(f'gpi{i}',
                           coordinate=True,
                           pos=RelativeAnchor('gpi', j))
            for i, j in angles(0, 3):
                g.add_node(f'gpep{i}',
                           coordinate=True,
                           pos=RelativeAnchor('gpep', j))
            for i, j in angles(-90, 3, 50):
                g.add_node(f'gpen{i}',
                           coordinate=True,
                           pos=RelativeAnchor('gpen', j))
            for i, j in angles(90, 3):
                g.add_node(f'sncd{i}',
                           coordinate=True,
                           pos=RelativeAnchor('sncd', j))
            for name in 'id':
                for i, j in angles(180 if name == 'd' else 0, 2):
                    g.add_node(f'strp{name}{i}',
                               coordinate=True,
                               pos=RelativeAnchor(f'strp{name}', j))
            for i, j in angles(90, 3):
                g.add_node(f'sncv{i}',
                           coordinate=True,
                           pos=RelativeAnchor('sncv', j))
            for i, j in angles(-90, 3):
                g.add_node(f'below_sncv{i}',
                           coordinate=True,
                           pos=RelativeAnchor('sncv', j))
            for s in ['strmi', 'strmd']:
                for i in [0, 1]:
                    g.add_node(s + '_' + str(i),
                               coordinate=True,
                               relpos=(0.3 * (2 * i - 1), 0,
                                       RelativeAnchor(s, 'south')))
            # Subthalamic links.
            i = 0
            for y in [f'gpep{i}',
                      f'gpi{2 - i}',
                      f'gpen{1 + i}',
                      f'below_sncv{i}']:
                if y.startswith('gpen'):
                    to = 'explanation'
                    via = [f'gpep{i}']
                elif y.startswith('below_sncv'):
                    to = 'intention'
                    via = [f'gpi{2 - i}']
                else:
                    to = 'demand'
                    via = []
                g.add_edge('stn', y,
                           to=to,
                           via=(True, via, D),
                           opacity=opacity(['stn']))
            g.add_edge('stn', 'sncd',
                       to='pooling',
                       opacity=opacity(['stn']))
            g.add_edge('gpen2', 'stn',
                       to='explanation_in',
                       via=(True, [], D),
                       opacity=opacity(['stn']))

            # Striato-nigral links.
            for i, y in enumerate(['strpd', 'strpi']):
                g.add_edge(f'{y}{1 - i}', f'sncv{2 * i}',
                           to=f'explanation{"_in" if i else ""}',
                           via=(False, [], D),
                           opacity=opacity(['strp']))
            g.add_edge('strm_sncd2',
                       'sncd2',
                       to='explanation',
                       opacity=opacity(['strm']))

            # Nigro-striatal links.
            for i, x in enumerate(['strpi', 'strpd']):
                to = 'regret' if i == 0 else 'regret'
                g.add_edge('sncv1',
                           f'{x}{1 - i}',
                           to=to,
                           via=(True, [], D),
                           opacity=opacity(['strp']))
            g.add_edge('sncd0',
                       'strm_sncd0',
                       to='forgetting',
                       opacity=opacity(['strm']))

            # Striato-striatal links.
            g.add_edge('strp', 'strm',
                       to='realization',
                       opacity=opacity([]))

            # Striato-pallidal links.
            g.add_edge('striatum_gpen', 'gpen',
                       to='explanation_in',
                       opacity=opacity(['strm']))
            for x, y in (['strmi_0', 'gpep'], ['strmd_1', 'gpi']):
                g.add_edge(x,
                           y,
                           to='demand_in',
                           opacity=opacity(['strm']),
                           via=(True, [], D))
            for x, y in (['strpi', 'gpep'], ['strpd', 'gpi']):
                g.add_edge(x,
                           y,
                           to='realization',
                           opacity=opacity(['strp']))

            # Cortico-striatl links.
            g.add_edge('ctxpt', 'strm',
                       to='explanation',
                       opacity=opacity(['strm']),
                       via=(True,
                            ['str_above'],
                            D))
            g.add_edge('ctxit', 'striatum_ctxit',
                       to='pooling',
                       dash='dashed',  # diffuse
                       opacity=opacity(['strm']))

            # Nigral afferents.
            g.add_edge('sncv', 'sncd',
                       to='onset',
                       opacity=opacity([]))
            g.add_edge('reward',
                       'below_sncv1',
                       to='pooling',
                       opacity=opacity([]))

            # Pallido-nigral link.
            g.add_edge('gpi0',
                       'below_sncv2',
                       to='explanation_in',
                       via=(False, [], D),
                       opacity=opacity(['strm']))

            # Pallidal links.
            g.add_edge('gpep1', 'gpen0',
                       to='explanation_in',
                       via=(False, [], D),
                       opacity=opacity(['strm']))
            g.add_edge('gpep1', 'gpi1',
                       to='explanation_in',
                       opacity=opacity(['strm']))

            # Hyper-direct pathway.
            g.add_edge('ctxpt', 'stn',
                       to='pooling',
                       opacity=opacity(['stn']),
                       via=(True,
                            ['str_above', 'right_of_everything'],
                            D))

            # Basal ganglia outputs.
            for x, y in (('gpi', 'tha'), ('gpep', 'thf'), ):
                g.add_edge(x, y,
                           to='output',
                           opacity=opacity(['strm']))

            network.fix_opacity()
            network.generate(f)
