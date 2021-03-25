from typing import Container

from edge_colors import EDGE_COLORS

from tikzify import (Alignment, Edge, IntersectionAnchor, NodeAnchor, NodeContainer, NodeGraph,
                     NodePosition, NodeText, RelativeAnchor, TerminalSpacing, TextSize, tex_file,
                     tex_pic)

dimmed_opacity = 0.18
node_size = (13.0, 11.0)
w = 0.8
terminal_spacing = TerminalSpacing(horizontal=[0.0, 0.8, w / 2, w / 3, w / 4, w / 5],
                                   vertical=[0.0, 0.5, 0.4, 0.3])


def opacity(groups: Container[str]) -> float:
    return (1.0
            if opaque_group in groups or opaque_group == 'all'
            else dimmed_opacity)


with tex_file('basal_ganglia.tex',
              ['latex/includes',
               'latex/commands',
               'tikz/base',
               'tikz/color_macros',
               'tikz/extra_tips',
               'tikz/cma_tips',
               'tikz/flow_style']) as f:
    for opaque_group in ['all',
                         # 'strp',
                         # 'strm',
                         # 'stn',
                         ]:
        node_graph = NodeGraph(edge_colors=EDGE_COLORS)

        def create_rectangular_node(name: str,
                                    position: NodePosition,
                                    text: NodeText) -> None:
            node_graph.create_node(name, position, text=text, size=node_size, shape='rectangle')

        g = node_graph.digraph
        with tex_pic(f,
                     'basal_ganglia-' + opaque_group,
                     'Flow diagram, /CMA tips'):
            # Create nodes.
            mx, my = 5.5, 2.7
            y = 2.4
            for name, direction in [('strmi', 'left'), ('strmd', 'right')]:
                d = {direction: 5.5}
                create_rectangular_node(name,
                                        NodePosition(NodeAnchor('str_center'), above=y, **d),
                                        text=NodeText([rf'$\{name}$']))
            for name, direction in [('strpi', 'left'), ('strpd', 'right')]:
                d = {direction: 4.0}
                create_rectangular_node(name,
                                        NodePosition(NodeAnchor('str_center'), **d),
                                        text=NodeText([rf'$\{name}$']))
            create_rectangular_node('sncd',
                                    NodePosition(NodeAnchor('str_center'), below=2.5),
                                    text=NodeText([r'$\sncd$']))
            create_rectangular_node('gpen',
                                    NodePosition(NodeAnchor('sncd'), left=2.5),
                                    text=NodeText([r'$\gpen$']))
            create_rectangular_node('sncv',
                                    NodePosition(NodeAnchor('sncd'), right=2.5),
                                    text=NodeText([r'$\sncv$']))
            create_rectangular_node('gpi',
                                    NodePosition(IntersectionAnchor('strpd', 'gpi_center')),
                                    text=NodeText([r'$\gpi$']))
            create_rectangular_node('gpep',
                                    NodePosition(IntersectionAnchor('strpi', 'gpi_center')),
                                    text=NodeText([r'$\gpep$']))
            create_rectangular_node('stn',
                                    NodePosition(NodeAnchor('sncd'), below=3.6),
                                    text=NodeText([r'$\stn$']))
            create_rectangular_node('tha',
                                    NodePosition(NodeAnchor('gpi'), right=2.5),
                                    text=NodeText([r'$\tha$']))
            for name, vertical in (('ctxit', 'gpen'), ('ctxpt', 'sncv')):
                create_rectangular_node(name,
                                        NodePosition(IntersectionAnchor(vertical, 'ctx_center')),
                                        text=NodeText([rf'$\{name}$']))

            # Create inputs and outputs.
            node_graph.create_io('reward',
                                 NodeText(['reward', 'input'],
                                          align=Alignment.center, color='dcolorr',
                                          size=TextSize.footnote, standard_height=True),
                                'bottom_edge',
                                'below_sncv1')
            node_graph.create_io('policy',
                                 NodeText(['policy', 'input'],
                                          align=Alignment.center, color='dcolorb',
                                          size=TextSize.footnote, standard_height=True),
                                'bottom_edge',
                                'below_tha0')

            # Create containers.
            for name, text, group in [('striatum', 'Striatum', [f'str{b}{a}'
                                                                for a in 'di'
                                                                for b in 'mp']),
                                      ('strp', 'Striatal patch', [f'strp{a}' for a in 'di']),
                                      ('strm', 'Striatal matrix', [f'strm{a}' for a in 'di']),
                                      # ('snc', 'SNc', ['sncd', 'sncv']),
                                      ]:
                node_graph.create_node(name,
                                       None,
                                       container=NodeContainer(
                                           group,
                                           corner_text=NodeText([text], size=TextSize.footnote)),
                                       inner_sep=12 if name=='striatum' else 5,
                                       shape='rectangle, draw',
                                       color='dcolorr',
                                       dash='dashed')

            # Create terminals.
            node_graph.create_node_terminals('ctxit', terminal_spacing, 0, 0, 0, 2)
            node_graph.create_node_terminals('ctxpt', terminal_spacing, 0, 2, 0, 4)
            node_graph.create_node_terminals('gpi', terminal_spacing, 3, 2, 1, 0)
            node_graph.create_node_terminals('gpep', terminal_spacing, 1, 3, 1, 1)
            node_graph.create_node_terminals('gpen', terminal_spacing, 0, 0, 1, 3)
            node_graph.create_node_terminals('sncv', terminal_spacing, 1, 0, 4, 3)
            node_graph.create_node_terminals('sncd', terminal_spacing, 0, 1, 2, 1)
            node_graph.create_node_terminals('strpi', terminal_spacing, 0, 0, 0, 1)
            node_graph.create_node_terminals('strpd', terminal_spacing, 0, 0, 0, 1)
            node_graph.create_node_terminals('strmi', terminal_spacing, 0, 0, 0, 1)
            node_graph.create_node_terminals('strmd', terminal_spacing, 0, 0, 0, 1)
            node_graph.create_node_terminals('stn', terminal_spacing, 1, 1, 5, 0)
            node_graph.create_node_terminals('tha', terminal_spacing, 2, 1, 0, 1)

            # Create coordinates.
            for group, anchor, horizontal, name in [
                ('strm', 'north', 'below_ctxit0', 'strm_ctxit'),
                ('strp', 'north', 'below_ctxit1', 'strp_ctxit'),
                ('strm', 'north', 'below_ctxpt3', 'strm_ctxpt'),
                ('striatum', 'south', 'above_gpen0', 'striatum_gpen'),
                ('strm', 'south', 'above_sncd0', 'strm_sncd0'),
                ('strm', 'south', 'above_sncd1', 'strm_sncd1'),
                ('strm', 'south', 'above_sncv1', 'strm_sncv1'),
                ('strp', 'south', 'above_sncv2', 'strp_sncv2'),
                ('strp', 'south', 'above_sncv3', 'strp_sncv3'),
                ('strm', 'south', 'strpi', 'below_strm'),
                ('strp', 'north', 'strpi', 'above_strp'),
            ]:
                node_graph.create_coordinate(
                    name,
                    NodePosition(IntersectionAnchor(horizontal, RelativeAnchor(group, anchor))))
            node_graph.create_coordinate('str_center', (0, 0))
            node_graph.create_coordinate('ctx_center',
                                         NodePosition(NodeAnchor('str_center'), above=6.0))
            node_graph.create_coordinate('gpi_center', NodePosition(NodeAnchor('sncd'), below=2.0))
            node_graph.create_coordinate(
                'thalamo_cortical0',
                NodePosition(RelativeAnchor('striatum', 'east'), right=0.4))
            node_graph.create_coordinate(
                'thalamo_cortical1',
                NodePosition(NodeAnchor('thalamo_cortical0'), right=0.4))
            node_graph.create_coordinate('str_above',
                                         NodePosition(RelativeAnchor('striatum', 'north'),
                                                      above=0.3))
            node_graph.create_edges('striatum', 'thalamo_cortical1', 'ctxpt', 'stn', margin=0.85)

            # --------------------------------------------------------------------------------------
            # Subthalamic links.
            for source, target, to in [('above_stn0', 'right_of_gpep0', 'demand'),
                                       ('above_stn4', 'left_of_gpi0', 'demand'),
                                       ('above_stn1', 'below_gpen2', 'pooling'),
                                       ('above_stn3', 'below_sncv0', 'pooling_presence')]:
                via = ['right_of_gpep2'] if target.startswith('below') else []
                node_graph.create_edge(source, target, Edge(to=to, opacity=opacity(['stn'])),
                                       via=(True, via))
            node_graph.create_edge('above_stn2', 'below_sncd0',
                                   Edge(to='pooling', opacity=opacity(['stn'])))

            # --------------------------------------------------------------------------------------
            # Nigro-cortical links.
            node_graph.create_edge('above_sncv0', 'below_ctxpt0',
                                    Edge(to='co_prediction', opacity=opacity(['strp'])))

            # Nigro-striatal links.
            node_graph.create_edge('above_sncv1', 'strm_sncv1',
                                    Edge(to='co_prediction', opacity=opacity(['strp'])))
            node_graph.create_edge('above_sncv2', 'strp_sncv2',
                                    Edge(to='co_explanation', opacity=opacity(['strp'])))
            node_graph.create_edge('above_sncd0', 'strm_sncd0',
                                   Edge(to='demand', opacity=opacity(['strm'])))

            # Nigro-nigral link.
            node_graph.create_edge('left_of_sncv0', 'right_of_sncd0',
                                   Edge(to='co_demand', opacity=opacity([])))

            # --------------------------------------------------------------------------------------
            # Striato-nigral links.
            node_graph.create_edge('strp_sncv3', 'above_sncv3',
                                    Edge(to='explanation', opacity=opacity(['strp'])))
            node_graph.create_edge('strm_sncd1', 'above_sncd1',
                                   Edge(to='prediction', opacity=opacity(['strm'])))

            # Striato-striatal links.
            node_graph.create_edge('above_strp', 'below_strm',
                                   Edge(to='co_prediction', opacity=opacity([])))

            # Striato-pallidal links.
            node_graph.create_edge('striatum_gpen', 'above_gpen0',
                                   Edge(to='explanation', opacity=opacity(['strm'])))
            for source, target in [('below_strmi0', 'left_of_gpep0'),
                                   ('below_strmd0', 'right_of_gpi1')]:
                node_graph.create_edge(source, target,
                                       Edge(to='prediction', opacity=opacity(['strm'])),
                                       via=(True, []))
            for source, target in [('below_strpi0', 'above_gpep0'),
                                   ('below_strpd0', 'above_gpi0')]:
                node_graph.create_edge(source, target,
                                       Edge(to='explanation', opacity=opacity(['strp'])))

            # --------------------------------------------------------------------------------------
            # Pallido-nigral link.
            node_graph.create_edge('left_of_gpi2', 'below_sncv2', Edge(to='gln',
                                                                       opacity=opacity(['strm'])),
                                   via=(False, []))

            # Pallido-pallidal links.
            node_graph.create_edge('right_of_gpep2', 'below_gpen0',
                                   Edge(to='gln', opacity=opacity(['strm'])),
                                   via=(False, []))
            node_graph.create_edge('right_of_gpep1', 'left_of_gpi1',
                                   Edge(to='prediction', opacity=opacity(['strm'])))

            # Pallido-thalamic link.
            node_graph.create_edge('right_of_gpi0', 'left_of_tha0',
                                   Edge(to='selection', opacity=opacity(['strm'])))

            # Pallido-subthalamic link.
            node_graph.create_edge('below_gpen1', 'left_of_stn0',
                                   Edge(to='demand', opacity=opacity(['stn'])),
                                   via=(True, []))

            # --------------------------------------------------------------------------------------
            # Cortico-striatal links.
            node_graph.create_edge('below_ctxpt3', 'strm_ctxpt',
                                   Edge(to='pooling', opacity=opacity(['strm'])))
            # Dashed lines indicates a diffuse link.
            node_graph.create_edge('below_ctxit0', 'strm_ctxit',
                                   Edge(to='demand', dash='densely dashdotted',
                                        opacity=opacity(['strm'])))
            node_graph.create_edge('below_ctxit1', 'strp_ctxit',
                                   Edge(to='selection', dash='densely dashdotted',
                                        opacity=opacity(['strm'])))

            # Hyper-direct pathway.
            node_graph.create_edge('right_of_ctxpt1', 'right_of_stn0',
                                   Edge(to='pooling', opacity=opacity(['stn'])),
                                   via=(False, ['thalamo_cortical1']))

            # --------------------------------------------------------------------------------------
            # Thalamo-cortical link.
            node_graph.create_edge('right_of_tha0', 'right_of_ctxpt0',
                                   Edge(to='gln', opacity=opacity(['strm'])),
                                   via=(False, ['thalamo_cortical0']))

            # Exogenous signals.
            node_graph.create_edge('reward', 'below_sncv1',
                                   Edge(to='pooling_value', opacity=opacity([])))
            node_graph.create_edge('policy', 'below_tha0',
                                   Edge(to='prediction', opacity=opacity([])))

            node_graph.generate(f)
